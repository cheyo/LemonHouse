TRUNCATE TABLE house_companystat;
INSERT INTO house_companystat(company,project_count,house_count,size_count) 
SELECT house_project.company,COUNT(DISTINCT(house_project.id)),COUNT(house_house.id),SUM(house_house.size1)
FROM house_branch INNER JOIN house_project ON house_branch.project_id = house_project.id
INNER JOIN house_house ON house_house.branch_id = house_branch.id
GROUP BY house_project.company;
