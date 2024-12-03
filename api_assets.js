//
// app.get('/assets', async (req, res) => {...});
//
// Return all the assets from the database:
//
const photoapp_db = require('./photoapp_db.js')

//
// query_database:
//
// Queries database, returning a PROMISE that you can
// await on. When the PROMISE resolves, you'll have the 
// results of your query (or you'll get an error thrown
// back).
//
function query_database(db, sql)
{
  let response = new Promise((resolve, reject) => {
    try 
    {
      //
      // execute the query, and when we get the callback from
      // the database server, either resolve with the results
      // or error with the error object
      //
      db.query(sql, (err, results, _) => {
        if (err) {
          reject(err);
        }
        else {
          resolve(results);
        }
      });
    }
    catch (err) {
      reject(err);
    }
  });
  
  // 
  // return the PROMISE back to the caller, which will
  // eventually resolve to results or an error:
  //
  return response;
}

exports.get_assets = async (req, res) => {

  console.log("**Call to get /assets...");

  try {

    
    //throw new Error("TODO: /assets");

    let sql = 'SELECT * FROM assets ORDER BY assetid ASC';

    console.log("/assets: calling RDS to get asset details...");

    // Query the database using the helper function
    const results = await query_database(photoapp_db, sql);

    // Respond with the results
    res.json({
      "message": "success",
      "data": results
    });
    
               

    //
    // TODO: remember we did an example similar to this in class with
    // movielens database
    //
    // MySQL in JS:
    //   https://expressjs.com/en/guide/database-integration.html#mysql
    //   https://github.com/mysqljs/mysql
    //
    

  }//try
  catch (err) {
    console.log("**Error in /assets");
    console.log(err.message);
    
    res.status(500).json({
      "message": err.message,
      "data": []
    });
  }//catch

}//get
