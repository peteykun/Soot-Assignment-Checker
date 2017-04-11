<!doctype html>
<html lang="en">
  <head>
    <meta charset="utf-8">
    <meta http-equiv="X-UA-Compatible" content="IE=edge">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <!-- The above 3 meta tags *must* come first in the head; any other head content must come *after* these tags -->
    <title>SRT Utility</title>

    <!-- Bootstrap -->
    <link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/bootstrap/3.3.7/css/bootstrap.min.css" integrity="sha384-BVYiiSIFeK1dGmJRAkycuHAHRg32OmUcww7on3RYdg4Va+PmSTsz/K68vbdEjh4u" crossorigin="anonymous">

    <style>
    body {
      padding-top: 50px;
    }
    </style>

    <!-- HTML5 shim and Respond.js for IE8 support of HTML5 elements and media queries -->
    <!-- WARNING: Respond.js doesn't work if you view the page via file:// -->
    <!--[if lt IE 9]>
      <script src="https://oss.maxcdn.com/html5shiv/3.7.3/html5shiv.min.js"></script>
      <script src="https://oss.maxcdn.com/respond/1.4.2/respond.min.js"></script>
    <![endif]-->
  </head>
  <body>
    <nav class="navbar navbar-inverse navbar-fixed-top">
      <div class="container">
        <div class="navbar-header">
          <a class="navbar-brand" href="/">SRT Submission Utility</a>
          <ul class="nav navbar-nav">
            <li class="active"><a href="/">Home</a></li>
            <li><a href="/submissions">Submissions</a></li>
% if logged_in:
            <li><a href="/logout">Logout</a></li>
%end
          </ul>
        </div>
      </div>
    </nav>

    <div class="container">

      <div class="starter-template">

% if logged_in:

        <h1>SRT Submission Utility</h1>
        <p class="lead">Use this form to submit your assignment. Pick the test suite you want to run on.</p>

        <form action="/run" method="POST" enctype="multipart/form-data">
% if error == '':
          <div class="alert alert-warning"><b>Heads up!</b> Make sure you export a runnable JAR.</div>
% else:
          <div class="alert alert-danger"><b>Error:</b> {{error}}</div>
% end

          <input type="hidden" name="name" value="{{username}}">

          <div class="form-group">
            <label for="suite">Test Suite</label>
            <select name="suite" class="form-control">
              <option value="SampleTests">SampleTests.jar</option>
              <option value="PrivateSmallTests">PrivateSmallTests.jar</option>
              <option value="PrivateLargeTest">PrivateLargeTest.jar</option>
              <option value="ExtraTests">ExtraTests.jar</option>
            </select>
          </div>

          <div class="form-group">
            <label class="control-label">Pick your JAR file</label>
            <input name="jar" type="file" class="file">
          </div>

          <br>

          <div class="form-group">
            <input type="submit" class="btn btn-success" value="Queue submission">
          </div>
        </form>

% else:
        <h1>Log in</h1>
        <p class="lead">Use this form to log in.</p>

        <form action="/login" method="POST">
% if error != '':
          <div class="alert alert-danger"><b>Error:</b> {{error}}</div>
% end

          <div class="form-group">
            <label for="name">Name</label>
            <select name="name" class="form-control">
              <option value="" selected></selected>
              <option value="Aayush_Moroney">Aayush Moroney</option>
              <option value="Akshay_Jain">Akshay Jain</option>
              <option value="Manoharan">Manoharan</option>
              <option value="Nikita_Chopra">Nikita Chopra</option>
              <option value="Patil_Ketan_Prabhakar">Patil Ketan Prabhakar</option>
              <option value="Ronit_Halder">Ronit Halder</option>
              <option value="Subhendu_Malakar">Subhendu Malakar</option>
              <option value="Ullas_Aparanji">Ullas Aparanji</option>
              <option value="admin">Team Rocket</option>
            </select>
          </div>

          <div class="form-group">
            <label for="password">Password</label>
            <input type="password" class="form-control" name="password">
          </div>

          <br>

          <div class="form-group">
            <input type="submit" class="btn btn-success" value="Log in">
          </div>
        </form>
% end

      </div>

    </div><!-- /.container -->

    <!-- jQuery (necessary for Bootstrap's JavaScript plugins) -->
    <script src="https://ajax.googleapis.com/ajax/libs/jquery/1.12.4/jquery.min.js"></script>
    <!-- Include all compiled plugins (below), or include individual files as needed -->
    <script src="https://maxcdn.bootstrapcdn.com/bootstrap/3.3.7/js/bootstrap.min.js" integrity="sha384-Tc5IQib027qvyjSMfHjOMaLkfuWVxZxUPnCJA7l2mCWNIpG9mGCD8wGNIcPD7Txa" crossorigin="anonymous"></script>
  </body>
</html>
