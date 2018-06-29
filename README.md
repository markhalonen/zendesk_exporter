# zendesk_exporter
Exports data from Zendesk API to excel or csv

# Install
1. Open a command prompt and run 

   `sudo easy_install pip`

   pip is a tool that lets python developers share code.
2. Now, run 

   `pip install zendesk_exporter`
   
   This installs the exporter to your computer
3. Now, run 

   `zendesk_exporter job_file.json`
   
   `job_file.json` is a file that the program needs to be able to find. `job_file.json` should look like this:

```json
{
    "domain_name": "XXX",
    "email": "XXX",
    "api_key": "XXX",
    "start_date": "2018-06-27",
    "end_date": "2018-06-30",
    "fetch_comments": true,
    "output_file_name": "last_6_months",
    "output_file_type": "csv",
    "fetch_all_ticket_data": false
}
```
You can change the parameters in this file to change how the program behaves. 