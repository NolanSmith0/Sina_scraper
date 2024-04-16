# Sina_scraper
a simple python scraper for sina, one of the most important social medias in China, like twitter
---

$$User Guide$$

  To use the code ```sina_scraper.py```, you need first add your sina account cookies to the folder ```/headers```. To do this, you can copy your sina cookies into python dic then use joblib save it(I did this for parallel speeding convinence), or you can directly modify the following code in ```sina_scraper.py```:

```python
# Turn the following code :
headers = []

for file in os.listdir('./headers/'):
    headers.append(joblib.load('./headers/' + file))

# into your own cookies
headers = [
        {'Cookies' : # your cookies 1 here},
        {'Cookies' : # your cookies 2 here}
]
```

After seeting up the cookies, find the user name and id of the account you want to scrape, then add them into global variables like following:

```python
UID = 2813700891
user_name = '微博基金'
begin_time = '2024-01-21'
end_time = '2024-01-31'
```
Then just run the function ```get_weibo_parallel(UID, splitted, headers)```, it will return a list of dics, each of one of them is one sina post, you can save it use pandas or anything you want.
