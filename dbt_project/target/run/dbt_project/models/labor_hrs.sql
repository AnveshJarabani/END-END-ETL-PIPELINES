
  create view "uct_data"."public"."labor_hrs__dbt_tmp"
    
    
  as (
    -- Active: 1688765630308@@localhost@5432@uct_data@public
SELECT
    *
FROM
    raw_lbr
WHERE
    "PART_NUMBER" != '#'
  );