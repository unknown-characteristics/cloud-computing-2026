SET SERVEROUTPUT ON;

create or replace trigger CONTESTANTS_INSERT
before insert on CONTESTANTS
for each row
begin
    if(:new.id is null) then
        :new.id := CONTESTANTS_ID_SEQ.nextval;
    end if;
end;

/

create or replace trigger CONTESTS_INSERT
before insert on CONTESTS
for each row
declare
    v_current_time TIMESTAMP;
begin 
    SELECT sysdate INTO v_current_time FROM DUAL;
    if(:new.start_time is null) then
        :new.start_time := v_current_time;
    end if;

    if(:new.status = 'ended' and :new.end_time is null) then
        :new.end_time := v_current_time;
    elsif (:new.status != 'ended') then
        :new.end_time := null;
    end if;

    if(:new.id is null) then
        :new.id := CONTESTS_ID_SEQ.nextval;
    end if;
end;

/

create or replace trigger CONTESTS_CHECK_STATUS
before update on CONTESTS
for each row
declare
    v_current_time TIMESTAMP;
begin
    if(UPDATING('start_time')) then
        raise_application_error(-20201, 'Cannot modify start time');
    end if;

    if(:old.status = 'ended') then
        if(:old.status != :new.status or :old.name != :new.name or :old.difficulty != :new.difficulty or :old.solution != :new.solution) then
            raise_application_error(-20202, 'Cannot modify contest after ending it');
        end if;
    elsif(:new.status = 'ended' and :new.end_time is null) then
        select sysdate into v_current_time from dual;
        :new.end_time := v_current_time;
    end if;
end;

/

create or replace trigger CONTESTS_GRANT_AWARDS
after update on CONTESTS
for each row
declare
    v_best_prize_id INTEGER;
begin
    if(:new.status = 'ended' and :old.status = 'active') then
        for rec in (select rn, contestant_id from (select rownum as rn, contestant_id from submissions where contest_id = :new.id and answer = :new.solution order by submission_time asc)) loop
            begin
                select prize_id into v_best_prize_id from (select prize_id from prizes where contest_id = :new.id and remaining_qty > 0 order by estimated_value desc) where rownum < 2;

                if(v_best_prize_id is not null) then
                    insert into awards(contest_id, prize_id, contestant_id) values(:new.id, v_best_prize_id, rec.contestant_id); 
                end if;
                    
                EXCEPTION
                    WHEN NO_DATA_FOUND THEN
                        EXIT;
            end;
        end loop;
    end if;
end;

/

create or replace trigger PRIZES_INSERT
before insert on PRIZES
for each row
begin
    if(:new.prize_id is null) then
        :new.prize_id := PRIZES_ID_SEQ.nextval;
    end if;
end;

/

create or replace trigger AWARDS_INSERT_SUBTRACT_PRIZE_REMAINING_QTY
before insert on AWARDS
for each row
begin
    UPDATE PRIZES SET remaining_qty = remaining_qty - 1 WHERE contest_id = :new.contest_id AND prize_id = :new.prize_id;
end;

/

create or replace trigger AWARDS_DELETE_INCREMENT_PRIZE_REMAINING_QTY
after delete on AWARDS
for each row
begin
    UPDATE PRIZES SET remaining_qty = remaining_qty + 1 WHERE contest_id = :new.contest_id AND prize_id = :new.prize_id;
end;

/

create or replace trigger SUBMISSIONS_INSERT
before insert on SUBMISSIONS
for each row
declare
    v_current_time TIMESTAMP;
begin
    SELECT sysdate INTO v_current_time FROM DUAL; 
    if(:new.join_time is null) then
        :new.join_time := v_current_time;
    end if;

    if(:new.answer is not null and :new.submission_time is null) then
        :new.submission_time := v_current_time;
    elsif (:new.answer is null) then
        :new.submission_time := null;
    end if;
end;

/

create or replace trigger SUBMISSIONS_CHECK_ACTIVE_CONTEST
before insert or update on SUBMISSIONS
for each row
declare
    v_count INTEGER;
    v_status VARCHAR2(10);
    v_contest_id INTEGER;
begin
    if (INSERTING) then
        v_contest_id := :new.contest_id;
    else
        v_contest_id := :old.contest_id;
    end if;

    select count(*) into v_count from CONTESTS where id = v_contest_id;

    if(v_count > 0) then
        select status into v_status from CONTESTS where id = v_contest_id;
    end if;

    if(v_status is not null and v_status != 'active') then
        raise_application_error(-20002, 'Cannot join/submit contest after contest has ended');
    end if;
end;

/

create or replace trigger PRIZES_CHECK_ACTIVE_CONTEST
before insert or delete on PRIZES
for each row
declare
    v_count INTEGER;
    v_status VARCHAR2(10);
    v_contest_id INTEGER;
begin
    if (INSERTING) then
        v_contest_id := :new.contest_id;
    else
        v_contest_id := :old.contest_id;
    end if;
    select count(*) into v_count from CONTESTS where id = v_contest_id;

    if(v_count > 0) then
        select status into v_status from CONTESTS where id = v_contest_id;
    end if;

    if(v_status is not null and v_status != 'active') then
        raise_application_error(-20003, 'Cannot add/remove prizes after contest has ended');
    end if;
end;

/

create or replace trigger PRIZES_CHECK_ACTIVE_CONTEST_UPDATE
before update on PRIZES
for each row
declare
    v_count INTEGER;
    v_status VARCHAR2(10);
begin
    select count(*) into v_count from CONTESTS where id = :new.contest_id;

    if(v_count > 0) then
        select status into v_status from CONTESTS where id = :new.contest_id;
    end if;

    if(v_status is not null and v_status = 'ended' and (UPDATING('description') or UPDATING('initial_qty') or UPDATING('estimated_value'))) then
        raise_application_error(-20004, 'Cannot modify prizes after contest has ended');
    end if;

    -- if the contest has not ended we may want to change quantity of prizes, and since no prize has been awarded yet remaining must be equal to initial
    if(v_status = 'active') then
        :new.remaining_qty := :new.initial_qty;
    end if;
end;

/
