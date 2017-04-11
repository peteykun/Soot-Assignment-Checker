<!doctype html>
<html lang="en">
  <head>
% if output.strip() == '':
    <meta http-equiv="refresh" content="2">
% end
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
            <li><a href="/">Home</a></li>
            <li class="active"><a href="/submissions">Submissions</a></li>
% if logged_in:
            <li><a href="/logout">Logout</a></li>
%end
          </ul>
        </div>
      </div>
    </nav>

    <div class="container">

      <div class="starter-template">
        <h1>Results</h1>

        <table class="table table-striped">
          <thead>
            <th>Method Name</th>
            <th colspan="4">Path Edges</th>
            <th colspan="3">Leaks</th>
            <th>Results</th>
          </thead>
          <thead>
            <th></th>
            <th>F</th>
            <th>M</th>
            <th>E</th>
            <th>D</th>
            <th>F</th>
            <th>M</th>
            <th>E</th>
            <th></th>
          </thead>
          <tbody>
% for row in rows:
            <tr>
              <td>{{row[0]}}</td>
              <td>{{row[1]}}</td>
              <td>{{row[2]}}</td>
              <td>{{row[3]}}</td>
              <td>{{row[4]}}</td>
              <td>{{row[5]}}</td>
              <td>{{row[6]}}</td>
              <td>{{row[7]}}</td>
              <td>{{"Pass" if row[2] == 0 and row[3] == 0 and row[4] == 0 and row[6] == 0 and row[7] == 0 else "Fail"}}</td>
            </tr>
% end
          </tbody>
        </table>
      </div>
      <br>

      <h3>Output</h3>
      <pre style="height: 300px; overflow-y: scroll;">{{output}}</pre>

    </div><!-- /.container -->

    <!-- jQuery (necessary for Bootstrap's JavaScript plugins) -->
    <script src="https://ajax.googleapis.com/ajax/libs/jquery/1.12.4/jquery.min.js"></script>
    <!-- Include all compiled plugins (below), or include individual files as needed -->
    <script src="https://maxcdn.bootstrapcdn.com/bootstrap/3.3.7/js/bootstrap.min.js" integrity="sha384-Tc5IQib027qvyjSMfHjOMaLkfuWVxZxUPnCJA7l2mCWNIpG9mGCD8wGNIcPD7Txa" crossorigin="anonymous"></script>
  </body>
</html>
