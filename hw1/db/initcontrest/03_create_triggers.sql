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
declare
    v_old_qty INTEGER;
begin
    UPDATE PRIZES SET remaining_qty = remaining_qty - 1 WHERE contest_id = :new.contest_id AND prize_id = :new.prize_id;
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

-- create or replace trigger SUBMISSIONS_INSERT_CHECK_PARTICIPATION
-- before insert on SUBMISSIONS
-- for each row
-- declare
--     v_count INTEGER;
-- begin
--     SELECT count(*) INTO v_count FROM PARTICIPATIONS
-- end;

-- /

