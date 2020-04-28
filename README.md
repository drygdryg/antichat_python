# Python wrapper for https://forum.antichat.ru/
[![PyPI pyversions](https://img.shields.io/pypi/pyversions/antichat.svg)](https://pypi.python.org/pypi/antichat/)
[![PyPI license](https://img.shields.io/pypi/l/antichat.svg)](https://pypi.python.org/pypi/antichat/)
![PyPI - Downloads](https://img.shields.io/pypi/dm/antichat)
## Installing
```
pip install antichat
```
Or you can install from source with:
```
https://github.com/drygdryg/antichat_python.git
cd antichat_python
python setup.py install
```
## Using
### Client
```python
import antichat

client = antichat.Client(username='myusername', password='mypassword')
client.auth()

post_id = client.make_post(thread=12345, message='Hi there!')
client.delete_post(post_id=post_id, reason='No hello')
```
### Thread reader
```python
import antichat

threadreader = antichat.ThreadReader(thread_id=12345)

all_posts = threadreader.read()   # Read all posts sequentially
first_posts = threadreader.read(limit=20)   # Get only first 20 posts
last_posts = threadreader.read(offset=400)   # Skip first 400 posts
posts = threadreader.read(start_post=6789)   # Read from post ID 6789

page = threadreader.read_page(page=5)   # Read page #5
```
