TRUNCATE TABLE house_datastat;

INSERT INTO house_datastat(month,type,house_count,size_count) 
SELECT DATE_FORMAT(house_project.approved_date,'%Y%m'),house_house.type,COUNT(house_house.id),SUM(house_house.size1) 
FROM house_project INNER JOIN house_branch ON house_project.id = house_branch.project_id
  INNER JOIN house_house ON house_branch.id = house_house.branch_id
WHERE PERIOD_DIFF(DATE_FORMAT(now(),'%Y%m'), DATE_FORMAT(house_project.approved_date,'%Y%m')) >= 1 
  AND PERIOD_DIFF(DATE_FORMAT(now(),'%Y%m'), DATE_FORMAT(house_project.approved_date,'%Y%m')) <= 12
GROUP BY DATE_FORMAT(house_project.approved_date,'%Y%m'),house_house.type;
