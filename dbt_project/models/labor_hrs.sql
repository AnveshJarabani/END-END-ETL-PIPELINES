-- Active: 1688765630308@@localhost@5432@uct_data@public
SELECT
    *
FROM
    raw_lbr
WHERE
    "PART_NUMBER" != '#'