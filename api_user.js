//
// app.put('/user', async (req, res) => {...});
//
// Inserts a new user into the database, or if the
// user already exists (based on email) then the
// user's data is updated (name and bucket folder).
// Returns the user's userid in the database.
//
const photoapp_db = require('./photoapp_db.js')
const util = require('util');

exports.put_user = async (req, res) => {

  console.log("**Call to put /user...");

  try {

    let data = req.body;

    let email = data.email;
    let lastname = data.lastname;
    let firstname = data.firstname;
    let bucketfolder = data.bucketfolder;

    // Verify that required fields are provided
    if (!email || !lastname || !firstname || !bucketfolder) {
      res.status(400).json({
        "message": "missing required information"
      });
      return;
    }

    // Prepare query functions
    const query = util.promisify(photoapp_db.query).bind(photoapp_db);

    // Check if the user already exists
    let sql = `SELECT userid FROM users WHERE email = ?`;
    let results = await query(sql, [email]);

    let userid;
    let message;

    if (results.length === 0) {
      // User does not exist, insert new user
      sql = `INSERT INTO users (email, lastname, firstname, bucketfolder) VALUES (?, ?, ?, ?)`;
      let insertResult = await query(sql, [email, lastname, firstname, bucketfolder]);

      userid = insertResult.insertId;
      message = "inserted";

    } else {
      // User exists, update information
      userid = results[0].userid;

      sql = `UPDATE users SET lastname = ?, firstname = ?, bucketfolder = ? WHERE email = ?`;
      await query(sql, [lastname, firstname, bucketfolder, email]);

      message = "updated";
    }

    // Return the response with the correct message
    res.json({
      "userid": userid,
      "message": message
    });
    
	
	
	
  }//try
  catch (err) {
    console.log("**Error in /user");
    console.log(err.message);

    res.status(500).json({
      "message": err.message,
      "userid": -1
    });
  }//catch

}//put
