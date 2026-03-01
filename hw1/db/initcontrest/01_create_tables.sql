SET SERVEROUTPUT ON;

DROP TABLE SUBMISSIONS;
DROP TABLE AWARDS;
DROP TABLE PRIZES;
DROP TABLE CONTESTS;
DROP TABLE CONTESTANTS;

CREATE TABLE CONTESTS(
    id INTEGER PRIMARY KEY,
    name VARCHAR2(100) UNIQUE NOT NULL,
    difficulty NUMBER(3, 2) NOT NULL,
    solution VARCHAR2(100) NOT NULL,
    start_time TIMESTAMP NOT NULL,
    end_time TIMESTAMP,
    status VARCHAR2(10) NOT NULL,
    CONSTRAINT c_contests_valid_status CHECK(status = 'active' or status = 'ended'),
    CONSTRAINT c_contests_valid_time CHECK(start_time <= end_time)
);

CREATE TABLE CONTESTANTS(
    id INTEGER PRIMARY KEY,
    name VARCHAR2(100) NOT NULL,
    email VARCHAR2(100) UNIQUE NOT NULL,
    school VARCHAR2(100) NOT NULL
);

CREATE TABLE PRIZES(
    contest_id INTEGER NOT NULL,
    prize_id INTEGER NOT NULL,
    initial_qty INTEGER NOT NULL,
    remaining_qty INTEGER NOT NULL,
    description VARCHAR2(200) NOT NULL,
    estimated_value INTEGER NOT NULL,
    CONSTRAINT c_prize_remaining_valid CHECK(0 <= remaining_qty AND remaining_qty <= initial_qty),
    CONSTRAINT c_prize_fk_contest_id FOREIGN KEY(contest_id) REFERENCES CONTESTS(id),
    CONSTRAINT c_prize_pk_contest_prize_id PRIMARY KEY(contest_id, prize_id)
);

CREATE TABLE AWARDS(
    contest_id INTEGER NOT NULL,
    prize_id INTEGER NOT NULL,
    contestant_id INTEGER NOT NULL,
    CONSTRAINT c_award_fk_contest_prize_id FOREIGN KEY(contest_id, prize_id) REFERENCES PRIZES(contest_id, prize_id),
    CONSTRAINT c_award_fk_contest_id FOREIGN KEY(contest_id) REFERENCES CONTESTANTS(id),
    CONSTRAINT c_award_pk_all_ids PRIMARY KEY(contest_id, prize_id, contestant_id)
);

CREATE TABLE SUBMISSIONS(
    contest_id INTEGER NOT NULL,
    contestant_id INTEGER NOT NULL,
    answer VARCHAR2(100),
    join_time TIMESTAMP NOT NULL,
    submission_time TIMESTAMP,
    CONSTRAINT c_subm_fk_contest_id FOREIGN KEY(contest_id) REFERENCES CONTESTS(id),
    CONSTRAINT c_subm_fk_contestant_id FOREIGN KEY(contestant_id) REFERENCES CONTESTANTS(id),
    CONSTRAINT c_subm_pk_contest_contestant_id PRIMARY KEY(contest_id, contestant_id),
    CONSTRAINT c_subm_submit_after_join CHECK(submission_time >= join_time)
);

-- CREATE TABLE PARTICIPATIONS(
--     contest_id INTEGER NOT NULL,
--     contestant_id INTEGER NOT NULL,
--     join_time TIMESTAMP NOT NULL,
--     CONSTRAINT c_part_fk_contest_id FOREIGN KEY(contest_id) REFERENCES CONTESTS(id),
--     CONSTRAINT c_part_fk_contestant_id FOREIGN KEY(contestant_id) REFERENCES CONTESTANTS(id),
--     CONSTRAINT c_part_pk_contest_contestant_id PRIMARY KEY(contest_id, contestant_id)
-- );
