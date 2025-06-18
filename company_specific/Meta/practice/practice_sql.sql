-- DataLemur 

-- To find the Facebook pages that do not possess any likes. 
-- we can use the EXCEPT operator.
-- This operator allows us to subtract the rows from one result set that exist in another result set.
-- correlated sub query check what is better when 
Select page_id 
from pages 
where page_id not in (
select page_id
from page_likes);

SELECT pg.page_id
FROM pages as pg
LEFT OUTER JOIN page_likes AS likes
  ON pg.page_id = likes.page_id
WHERE likes.page_id IS NULL;

SELECT page_id
FROM pages
EXCEPT
SELECT page_id
FROM page_likes;

SELECT pg.page_id
FROM pages as pg
WHERE NOT EXISTS (
  SELECT page_id
  FROM page_likes AS likes
  WHERE likes.page_id = pg.page_id
);


-- Given a table of Facebook posts, for each user who posted 
-- at least twice in 2021, 
-- write a query to find the number of days between each user’s first post of the year and last post of the year in the year 2021. 
-- Output the user and number of the days between each user's first and last post.
SELECT user_id,
        max(post_date::date) - min(post_date::date) as days_between
FROM posts AS pg 
where DATE_PART('year', post_date::DATE) = 2021
group by user_id 
having count(post_id) >= 2 


SELECT user_id,
        max(post_date::date) - min(post_date::date) as days_between
FROM posts AS pg 
where Extract(year from post_date::DATE) = 2021
group by user_id 
having count(post_id) >= 2 ;

-- Date Part and Extract 
-- DATE_PART is a wrapper around EXTRACT
-- EXTRACT is slightly more efficient as it's a SQL standard function

-- SUM in CASE WHEN with GROUP BY 
-- Round syntax - use ::Numeric if using after AVG 

SELECT app_id, 
       ROUND( 100.0*
       SUM(case when event_type = 'click' then 1 else 0 end )/
       SUM(case when event_type = 'impression' then 1 else 0 end),2 ) as ctr 
FROM events
where EXTRACT( year from TIMESTAMP) = 2022
group by app_id;

-- division by integer might show you 0 for 0.6 so mul by 100.0
Select app_id, sum(click) as click,sum(impression) as impression, (100.0*sum(click))/sum(impression) 
from(
SELECT app_id, 
       case when event_type = 'click' then 1 else 0 end as click,
       case when event_type = 'impression' then 1 else 0 end as impression 
FROM events
where EXTRACT( year from TIMESTAMP) = 2022) a
group by app_id;



-- Write a query to obtain number of monthly active users (MAUs) in July 2022, including the month in numerical format "1, 2, 3".
-- Hint:
-- An active user is defined as a user who has performed actions such as 'sign-in', 'like', or 'comment' in both the current month and the previous month.
Select month_of_event as mth, 
       count(distinct user_id) as monthly_active_users
FROM
(Select user_id,
       month_of_event,
       Case when (LAG(last_event, 1) over (Partition BY user_id order by month_of_event) IS not 
      null ) then 1 else 0 end as active_in_month
from (
SELECT user_id,
       max(event_date) as last_event,
       EXTRACT(month from event_date)  as month_of_event 
FROM user_actions
where EXTRACT(year from event_date) = 2022
group by user_id, month_of_event) a
)b where active_in_month =1 and month_of_event = 7
GROUP by month_of_event;

SELECT 
  EXTRACT(MONTH FROM curr_month.event_date) AS mth, 
  COUNT(DISTINCT curr_month.user_id) AS monthly_active_users 
FROM user_actions AS curr_month
WHERE EXISTS (
  SELECT last_month.user_id 
  FROM user_actions AS last_month
  WHERE last_month.user_id = curr_month.user_id
    AND EXTRACT(MONTH FROM last_month.event_date) =
    EXTRACT(MONTH FROM curr_month.event_date - interval '1 month')
)
  AND EXTRACT(MONTH FROM curr_month.event_date) = 7
  AND EXTRACT(YEAR FROM curr_month.event_date) = 2022
GROUP BY EXTRACT(MONTH FROM curr_month.event_date);

-- FULL OUTER JOIN - clarifying question if that is needed or left join will work  
-- COALESCE  
SELECT 
  COALESCE(advertiser.user_id, daily_pay.user_id) AS user_id,
  CASE 
    WHEN paid IS NULL THEN 'CHURN' 
    WHEN paid IS NOT NULL AND advertiser.status IN ('NEW','EXISTING','RESURRECT') THEN 'EXISTING'
    WHEN paid IS NOT NULL AND advertiser.status = 'CHURN' THEN 'RESURRECT'
    WHEN paid IS NOT NULL AND advertiser.status IS NULL THEN 'NEW'
  END AS new_status
FROM advertiser
FULL OUTER JOIN daily_pay
  ON advertiser.user_id = daily_pay.user_id
ORDER BY user_id;

-- https://pgexercises.com/
-- OR vs IN
-- IN is better - readable , evaluated in hash 
select *
from cd.facilities 
where facid =1 or facid =5

-- Aggregate functions are not allowed in WHERE
-- You would like to get the first and last name of the last member(s) who signed up - not just the date. How can you do that?'
Select firstname, surname , joindate 
from cd.members
where joindate = (select max(joindate) as date
from cd.members) --subquery

-- OR 
select firstname, surname, joindate
	from cd.members
order by joindate desc
limit 1

-- Inner join syntax
SELECT starttime 
from cd.bookings as b
inner join cd.members as m 
on b.memid = m.memid
where m.firstname = 'David'
and m.surname = 'Farrell'
-- OR
select bks.starttime
        from
                cd.bookings bks,
                cd.members mems
        where
                mems.firstname='David'
                and mems.surname='Farrell'
                and mems.memid = bks.memid;

select distinct mem.firstname as firstname , mem.surname as surname
	from cd.members as rec
	inner join 
	cd.members as mem 
	on rec.recommendedby = mem.memid
order by surname, firstname;

-- Subqueries
select distinct concat(m.firstname, ' ', m.surname) as member,
       (select concat(recs.firstname, ' ', recs.surname) as recommender
		from cd.members as recs -- for each outer member inner is run to check who recommended them 
		where m.recommendedby = recs.memid)
from cd.members as m
order by member;

-- Postgres provides SERIAL types that are auto-filled with the next ID when you insert a row.
-- Cannot use VALUES as it accepts constant values, need to use SELECT
insert into cd.facilities
    (facid, name, membercost, guestcost, initialoutlay, monthlymaintenance)
    select (select max(facid) from cd.facilities)+1, 'Spa', 20, 30, 100000, 800; 

update cd.facilities 
set initialoutlay = 10000,
guestcost = 6
where initialoutlay = 8000
and name ='Tennis Court 2';	

[DDL constraints](https://www.postgresql.org/docs/current/ddl-constraints.html)

-- Why subqueries instead of joins?
-- Correlated subquery vs runs a large subquery once
delete from cd.members where memid not in (select memid from cd.bookings);          
delete from cd.members mems where not exists (select 1 from cd.bookings where memid = mems.memid);
