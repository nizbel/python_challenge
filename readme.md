# Python challenge

 This project reads a file and searches for IPs in 
 its contents, then performs Geo IP and RDAP 
 lookups for each IP found.
 
 ## How to use it
 
 ### Install requirements
 `pip install -r requirements.txt`
 
 ### Run challenge.py
 `python3 -m challenge --file your_text_file`
 
 ### Visualize data
 In order to visualize the data gathered from the text
 file, run 
```
python3 -m visualizer
```
 this command will run a simple http server, then 
 execute `files_read.html` in your browser of choice.
 This web page uses the `files_read.json` saved in
 the project's root folder to map the *json* files
 with the Geo IP and RDAP information collected for
 each filed that was read.
 
 ## Cache
 The cache implementation was a very basic *json* file
 storage, which by default handles up to 10000 entries.
 Once it goes above that amount, it drops the oldest
 entries.
 
 ### Cleaning cache files
 In case of corrupted info on the cache files, just
 delete the `.geocache` or `.rdapcache`