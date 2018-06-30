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
#### Parameters explained:
- `domain_name`: This is what appears in the url when you visit zendesk. `https://your-domain-name.zendesk.com`
- `email`: Your email address for authentication. 
- `api_key`: Your api key for authentication. This is basically a password.
- `start_date`: The _exclusive_ start date
- `end_date`: The _exclusive_ end date
- `fetch_comments`: Will download all the comments for all the tickets it finds. Can be time consuming.
- `output_file_name`: What to name the output file
- `output_file_type`: Options are `csv` or `excel`.
- `fetch_all_ticket_data`: Will download all ticket data. Can be time consuming.
