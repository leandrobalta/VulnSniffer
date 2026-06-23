#!/bin/bash 

repo_list=$1

while read line; do
    repo_link=$(echo $line | cut -d ',' -f 2)
    owner=$(echo $line | cut -d ',' -f 1 | cut -d '/' -f 1)
    project_name=$(echo $line | cut -d ',' -f 1 | cut -d '/' -f 2)
    folder_name="$owner-$project_name" 
    echo "$repo_link"
    echo "$owner"
    echo "$project_name"
    echo "$folder_name"
    git clone $repo_link ../src/mined_repos/$folder_name
    echo ""
done < $repo_list