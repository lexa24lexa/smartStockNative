# SmartStock - Retailer stock tracker 
*SmartStock* concerns retail inventory management activities within a chain of supermarkets. The system monitors product quantities, sales, refilling activities, and supplier shipments, while providing Smart Prediction Logic to optimize restocking decisions 

### **Developed by:**  
- (PM + FED) Alexandra Smirnova - 293835
- (BED) Álvaro Moreno - 293833
- (FED) Victor Alleon - 293877
- (BED) Martha Graham - 293853
- (BED) Francisco Marín - 293985
- (BED) Antonio Sánchez - 293982

### **Created with**

***Front-End***
- React Native + Native Web (TS)

***Back-End***
- Python

### **Installation guide**

***Front-End***

Inside of the frontend folder:
##### 1. 
npm install
##### 2. 
npm run web

npm run android

npm run ios # you need to use macOS to build the iOS project - use the Expo app if you need to do iOS development without a Mac

#### 3. 
you may need to install extra dependencies.

***Back-End***
##### 1. 
pip install fastapi uvicorn pymysql sqlalchemy

##### 2. 
pip install -r requirements.txt

##### 3. 
python -m uvicorn app.main:app --reload

##### 4. 
docker run --name retail-mysql \
  -e MYSQL_ALLOW_EMPTY_PASSWORD=yes \
  -e MYSQL_DATABASE=retail_bd \
  -p 3307:3306 \
  -v /path/to/backend:/docker-entrypoint-initdb.d \
  -d mysql:8

*Replace /path/to/backend with the absolute path to your backend folder.*