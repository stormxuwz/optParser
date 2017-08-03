import pycurl, json, StringIO

data = json.dumps({"image_url": "http://ubq.ubiaoqing.com/ubiaoqing3583d06d7a9989de1723e09b0050cf70.jpg"})
url = 'http://localhost/search'

storage = StringIO.StringIO()

c = pycurl.Curl()
c.setopt(c.URL, str(url))
c.setopt(c.PORT, 5000)
c.setopt(c.HTTPHEADER, ['Content-Type: application/json'])
c.setopt(pycurl.POST, 1)
c.setopt(pycurl.POSTFIELDS, data)
c.setopt(c.WRITEFUNCTION, storage.write)
c.perform()
c.close()

returned_json = storage.getvalue()
print returned_json
