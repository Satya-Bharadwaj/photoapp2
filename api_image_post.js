//
// app.post('/image/:userid', async (req, res) => {...});
//
// Uploads an image to the bucket and updates the database,
// returning the asset id assigned to this image.
//
const photoapp_db = require('./photoapp_db.js')
const util = require('util');
const { PutObjectCommand } = require('@aws-sdk/client-s3');
const { photoapp_s3, s3_bucket_name, s3_region_name } = require('./photoapp_s3.js');

const uuid = require('uuid');

exports.post_image = async (req, res) => {

  console.log("**Call to post /image/:userid...");

  try {

    let userid = req.params.userid;

    let data = req.body;  // data => JS object

    let assetname = data.assetname;
    let image_data = data.data;  // base64-encoded string

    if (!assetname || !image_data) {
      throw new Error("Missing required image data");
    }

    // Verify that the user exists in the database
    const query = util.promisify(photoapp_db.query).bind(photoapp_db);

    let sql = `SELECT * FROM users WHERE userid = ?`;
    let results = await query(sql, [userid]);

    if (results.length === 0) {
      res.status(400).json({
        "message": "no such user...",
        "assetid": -1
      });
      return;
    }

    // Proceed with image upload
    let user = results[0];
    let bucketfolder = user.bucketfolder;

    // Generate a unique key for the asset
    let bucket_key = `${bucketfolder}/${uuid.v4()}_${assetname}`;

    const buffer = Buffer.from(image_data, 'base64');

    let input = {
      Bucket: s3_bucket_name,
      Key: bucket_key,
      Body: buffer,
      ContentType: "image/jpeg",
      ACL: "public-read"
    };

    let command = new PutObjectCommand(input);
    await photoapp_s3.send(command);

    sql = `INSERT INTO assets (userid, assetname, bucketkey) VALUES (?, ?, ?)`;
    let result = await query(sql, [userid, assetname, bucket_key]);

    let assetid = result.insertId;

    res.json({
      "message": "success",
      "assetid": assetid
    });
    
	
	
	
  }//try
  catch (err) {
    console.log("**Error in /image");
    console.log(err.message);
    
    res.status(500).json({
      "message": err.message,
      "assetid": -1
    });
  }//catch

}//post
