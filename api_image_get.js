//
// app.get('/image/:assetid', async (req, res) => {...});
//
// Downloads an asset from S3 bucket and sends it back to the
// client as a base64-encoded string.
//
const photoapp_db = require('./photoapp_db.js')
const { GetObjectCommand } = require('@aws-sdk/client-s3');
const { photoapp_s3, s3_bucket_name } = require('./photoapp_s3.js');
const util = require('util');

exports.get_image = async (req, res) => {

  console.log("**Call to get /image/:assetid...");

  try {

    let assetid = req.params.assetid;

    const query = util.promisify(photoapp_db.query).bind(photoapp_db);

    let sql = `SELECT * FROM assets WHERE assetid = ?`;
    let results = await query(sql, [assetid]);

    if (results.length === 0) {
      res.status(400).json({
        "message": "no such asset...",
        "user_id": -1,
        "asset_name": "?",
        "bucket_key": "?",
        "data": []
      });
      return;
    }

    let asset = results[0];
    let user_id = asset.userid;
    let asset_name = asset.assetname;   // Corrected column name
    let bucket_key = asset.bucketkey;   // Corrected column name

    let input = {
      Bucket: s3_bucket_name,
      Key: bucket_key
    };

    let command = new GetObjectCommand(input);
    let response = await photoapp_s3.send(command);

    let datastr = await response.Body.transformToString("base64");

    res.json({
      "message": "success",
      "user_id": user_id,
      "asset_name": asset_name,
      "bucket_key": bucket_key,
      "data": datastr
    });

  }//try
  catch (err) {
    console.log("**Error in /image");
    console.log(err.message);

    res.status(500).json({
      "message": err.message,
      "user_id": -1,
      "asset_name": "?",
      "bucket_key": "?",
      "data": []
    });
  }//catch

}//get
