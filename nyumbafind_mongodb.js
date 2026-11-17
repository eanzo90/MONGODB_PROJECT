// NyumbaFind Uganda: MongoDB database setup and sample data
// Run this script in mongosh. It creates 4 collections with 5 documents each.

//db = db.getsiblingDB("nyumbaFindDB");

// Optional: uncomment the next line to reset the sample database before rerunning.
// db.dropDatabase();

// Create the four original collections
db.createCollection("users");
db.createCollection("properties");
db.createCollection("propertyReports");
db.createCollection("viewingRequests");

// 1. USERS: tenants, landlords, and property agents
db.users.insertMany([
  {_id:"U001",fullName:"Amina Nansubuga",phone:"+256700000001",role:"tenant",district:"Luwero",createdAt:ISODate("2026-10-01T09:00:00Z")},
  {_id:"U002",fullName:"Peter Ssemanda",phone:"+256700000002",role:"landlord",district:"Luwero",createdAt:ISODate("2026-10-02T10:30:00Z")},
  {_id:"U003",fullName:"Sarah Nakato",phone:"+256700000003",role:"agent",district:"Wakiso",createdAt:ISODate("2026-10-03T08:15:00Z")},
  {_id:"U004",fullName:"David Okello",phone:"+256700000004",role:"tenant",district:"Kampala",createdAt:ISODate("2026-10-04T12:00:00Z")},
  {_id:"U005",fullName:"Grace Atim",phone:"+256700000005",role:"landlord",district:"Mukono",createdAt:ISODate("2026-10-05T14:45:00Z")}
]);

// 2. PROPERTIES: rental properties advertised on the platform
db.properties.insertMany([
  {_id:"P001",title:"Two-bedroom house near Luwero Town",district:"Luwero",area:"Luwero Town",propertyType:"house",bedrooms:2,monthlyRentUGX:250000,depositUGX:250000,available:true,verificationStatus:"verified",advertiserId:"U002"},
  {_id:"P002",title:"Single room in Wakiso",district:"Wakiso",area:"Wakiso Town",propertyType:"single_room",bedrooms:1,monthlyRentUGX:100000,depositUGX:50000,available:true,verificationStatus:"pending",advertiserId:"U003"},
  {_id:"P003",title:"Three-bedroom family house",district:"Kampala",area:"Kawempe",propertyType:"house",bedrooms:3,monthlyRentUGX:600000,depositUGX:600000,available:true,verificationStatus:"verified",advertiserId:"U002"},
  {_id:"P004",title:"One-bedroom apartment",district:"Mukono",area:"Mukono Town",propertyType:"apartment",bedrooms:1,monthlyRentUGX:220000,depositUGX:220000,available:false,verificationStatus:"verified",advertiserId:"U005"},
  {_id:"P005",title:"Two-bedroom apartment in Kampala",district:"Kampala",area:"Ntinda",propertyType:"apartment",bedrooms:2,monthlyRentUGX:450000,depositUGX:300000,available:true,verificationStatus:"pending",advertiserId:"U003"}
]);

// 3. PROPERTY REPORTS: reports submitted by users for moderator review
db.propertyReports.insertMany([
  {_id:"R001",propertyId:"P002",reportedBy:"U001",reason:"Advertiser has not confirmed availability",status:"under_review",createdAt:ISODate("2026-10-06T09:00:00Z")},
  {_id:"R002",propertyId:"P003",reportedBy:"U004",reason:"Rental price may be inaccurate",status:"open",createdAt:ISODate("2026-10-06T11:20:00Z")},
  {_id:"R003",propertyId:"P005",reportedBy:"U001",reason:"Request for payment before viewing",status:"under_review",createdAt:ISODate("2026-10-07T08:30:00Z")},
  {_id:"R004",propertyId:"P004",reportedBy:"U004",reason:"Listing appears to be outdated",status:"resolved",createdAt:ISODate("2026-10-07T15:10:00Z")},
  {_id:"R005",propertyId:"P001",reportedBy:"U004",reason:"Please reconfirm the deposit amount",status:"open",createdAt:ISODate("2026-10-08T13:45:00Z")}
]);

// 4. VIEWING REQUESTS: tenants request appointments to view properties
db.viewingRequests.insertMany([
  {_id:"V001",propertyId:"P001",tenantId:"U001",requestedDate:ISODate("2026-10-16T09:00:00Z"),status:"confirmed",message:"I would like to view the house in the morning."},
  {_id:"V002",propertyId:"P002",tenantId:"U004",requestedDate:ISODate("2026-10-17T11:00:00Z"),status:"pending",message:"Please confirm whether the room is still available."},
  {_id:"V003",propertyId:"P003",tenantId:"U001",requestedDate:ISODate("2026-10-18T08:30:00Z"),status:"pending",message:"I want to view the house with my family."},
  {_id:"V004",propertyId:"P005",tenantId:"U004",requestedDate:ISODate("2026-10-19T13:00:00Z"),status:"cancelled",message:"I can no longer attend the viewing."},
  {_id:"V005",propertyId:"P001",tenantId:"U004",requestedDate:ISODate("2026-10-20T10:00:00Z"),status:"pending",message:"Please let me know the exact meeting point."}
]);

// Original indexes
db.users.createIndex({phone:1},{unique:true});
db.properties.createIndex({district:1,bedrooms:1,monthlyRentUGX:1});
db.properties.createIndex({available:1,verificationStatus:1});
db.propertyReports.createIndex({propertyId:1,status:1});
db.viewingRequests.createIndex({tenantId:1,status:1});

// Example queries
db.properties.find({district:"Luwero",bedrooms:2,monthlyRentUGX:{$lte:300000},available:true,verificationStatus:"verified"});
db.propertyReports.find({status:{$in:["open","under_review"]}});
db.viewingRequests.find({status:"pending"});

print("Users:",db.users.countDocuments());
print("Properties:",db.properties.countDocuments());
print("Property reports:",db.propertyReports.countDocuments());
print("Viewing requests:",db.viewingRequests.countDocuments());
