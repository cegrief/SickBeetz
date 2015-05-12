var Parse = require('parse').Parse;
var http = require('https');
var request = require('request');

var APP_ID = 'fp7oxuptKJ9ysesuXOeV4Ieul8ErSZklVwRslkJW';
var MASTER_KEY = 'HLpukqho21z1LaL7dUrPMRWI0jAu38NqmmL9qIfo';
Parse.initialize(APP_ID, MASTER_KEY);
//TODO: session token table

function checkUser(req, res, next){

    if(req.cookies.user!=undefined) {
        var user = JSON.parse(req.cookies.user);
        Parse.User.become(user.sessionToken, {
            success: function (res) {
                console.log('logged in with sessionToken');
                next();
            },
            error: function (err) {
                console.log('error logging in with sessionToken: ' + err);
            }
        });
    }
    console.log("not logged in");
    next();
}

module.exports = function (app) {
    //app.use(checkUser);
    var Secret = Parse.Object.extend("secrets");
    var Submissions = Parse.Object.extend("submissions");
    var Tokens = Parse.Object.extend("tokens");

    app.post("/api/secret/", function (req, res){
        console.log('submitting secret');
        var sec = new Secret();

        var mySecret = req.body.secret;
        mySecret.owner = Parse.User.current();
        mySecret.completed = 0;
        mySecret.submissions = 0;
        res.send(sec.save(mySecret));
    });

    app.get("/api/list", function(req, res){
        var query = new Parse.Query(Secret);
        query.find().then(function(results){
            res.send(results)
        });
    });

    app.get("/api/secret/:id", function(req, res){
        var query = new Parse.Query(Secret);
        query.include("owner");
        query.get(req.params.id,{}).then(function(r){
            console.log()
            r.attributes.username = r.get('owner').get('username');
            res.send(JSON.stringify(r));
        });
    });

    app.post("/api/submission/", function (req, res){

        var user = JSON.parse(req.cookies.user);
        console.log(req.body);
        var query = new Parse.Query(Secret);

        query.get(req.body.secret.objectId).then(function(r){
            r.increment("count");
            r.save();

            var sub = new Submissions();
            sub.set("secretId", r);
            sub.set("status", 'ip');
            sub.set("new", true);
            sub.set("body", req.body.submission);
            sub.set("image", req.body.img);
            sub.set("user", user.objectId);
            sub.set("secretOwner", req.body.secret.owner);

            res.send(sub.save(null,{}));
        });
    });

    app.post("/api/login/", function(req, res){
        Parse.User.logIn(req.body.username, req.body.password, {}).then(function(data) {
            var user = Parse.User.current();
            user.attributes.sessionToken = user._sessionToken;
            user = JSON.stringify(user);
            res.cookie('user', user, {expires: new Date(Date.now() + 86400000)});
            res.send(Parse.User.current());
        });
    });

    app.get("/api/known/", function(req, res){
        //TODO: Fix known, wanted, owned, review
        var query = new Parse.Query(Submissions);
        query.include("secretId");
        query.equalTo("status", "done");
        var user = JSON.parse(req.cookies.user);
        query.equalTo("user", user.objectId);
        query.find().then(function(r){
            var results = [];
            for(var i = 0; i< r.length; i++){
                results[i] = r[i].attributes.secretId;
            }
            res.send(results);
        });
    });

    app.get("/api/wanted/", function(req, res){
        var query = new Parse.Query(Submissions);
        query.include("secretId");
        query.notEqualTo("status", "done");
        query.equalTo("user", JSON.parse(req.cookies.user).objectId);
        query.find().then(function(r){
            var results = [];
            for(var i = 0; i< r.length; i++){
                results[i] = {
                    submission: r[i].attributes,
                    secret: r[i].attributes.secretId
                };
            }
            res.send(results);
        });
    });

    app.get("/api/owned/", function(req, res){
        var query = new Parse.Query(Secret);
        var user = JSON.parse(req.cookies.user);
        Parse.User.become(user.sessionToken).then(function(){
            query.equalTo("owner", Parse.User.current());
            query.find().then(function(r){
                res.send(r);
            });
        });
    });

    app.get("/api/review/", function(req,res){

        var user = JSON.parse(req.cookies.user);
        Parse.User.become(user.sessionToken).then(function(){
            var query = new Parse.Query(Submissions);
            query.equalTo("status", "ip");
            query.include('secretId');
            query.equalTo("secretOwner", Parse.User.current());
            query.find().then(function(r){
                var results = [];
                for(var i = 0; i< r.length; i++){
                    results[i] = {
                        submission: r[i].attributes,
                        secret: r[i].attributes.secretId,
                        submissionid: r[i].id
                    };
                }
                res.send(results);
            });
        });

    });

    app.post("/api/submission/approve", function(req,res){
        var query = new Parse.Query(Secret);
        var sub = req.body.submission;
        var upSub = new Submissions();

        //TODO fix updating completed count
        /*query.equalTo("objectId", sub.secretId);
         query.find().then(function(res){
         res[0].increment("completed");
         res[0].save();
         });*/
        upSub.set("status", "done");
        upSub.id = sub;
        upSub.save().then(function(r){
            res.send(r);
        });
    });
    //TODO:make sure the rest of these work with the parsefactory





    app.delete("/api/secret/", function(req, res){
        res.send(req.body.secret.destroy());
    });

    app.post("/api/submission/deny", function(req,res){
        var sub = req.body.submission;
        var upSub = new Submissions();

        upSub.set('status', 'denied');
        upSub.id = sub;
        upSub.save().then(function(r){
            res.send(r);
        });
    });

    app.get("/api/4square/", function(req,res){
        request('https://foursquare.com/oauth2/authenticate?client_id=15MIYO1ZBJHVKQOOJEPKR0DDL1N2BT20AETJCTU4LMF4QR2J&response_type=code&redirect_uri=http://secrets.ci.northwestern.edu/api/4squareCode')
    });

    app.get("/api/4squareCode/", function(req, res){
        request('https://foursquare.com/oauth2/access_token'
            + '?client_id=15MIYO1ZBJHVKQOOJEPKR0DDL1N2BT20AETJCTU4LMF4QR2J'
            + '&client_secret=31SV4VGK5K5AHQIMTW1B0YVANQYMIEQA4ICVMB5EDIWOYKRA'
            + '&grant_type=authorization_code'
            + '&redirect_uri=http://secrets.ci.northwestern.edu/api/4squareCode'
            + '&code=' + req.query.code, function(e, r, b){
                var sub = new Tokens();
                sub.set('4square', r.body.access_token);
                sub.save()
        });
    });

};
