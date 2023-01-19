# coding=utf-8

"""

Copyright(c) 2022-2023 Max Qian  <astroair.cn>

This library is free software; you can redistribute it and/or
modify it under the terms of the GNU Library General Public
License version 3 as published by the Free Software Foundation.
This library is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
Library General Public License for more details.
You should have received a copy of the GNU Library General Public License
along with this library; see the file COPYING.LIB.  If not, write to
the Free Software Foundation, Inc., 51 Franklin Street, Fifth Floor,
Boston, MA 02110-1301, USA.

"""

# #################################################################
# This file contains all of the html pages needed to create
# #################################################################

from flask import render_template,redirect
from flask_login import login_required

def create_html_page(app) -> None:
    """
        Create html pages 
        Args : 
            app : Flask application object
        Returns :
            None
    """

    @app.route('/',methods=['GET'])
    @app.route('/index',methods=['GET'])
    @app.route('/index.html',methods=['GET'])
    def index():
        return render_template('index.html')

    @app.route('/camera',methods=['GET'])
    @app.route('/camera/',methods=['GET'])
    @app.route('/camera.html',methods=['GET'])
    @login_required
    def camera():
        return render_template('camera.html')
        
    @app.route('/telescope',methods=['GET'])
    @app.route('/telescope/',methods=['GET'])
    @app.route('/telescope.html',methods=['GET'])
    @login_required
    def telescope():
        return render_template('telescope.html')

    @app.route('/focuser',methods=['GET'])
    @app.route('/focuser/',methods=['GET'])
    @app.route('/focuser.html',methods=['GET'])
    @login_required
    def focuser():
        return render_template('focuser.html')

    @app.route('/guider',methods=['GET'])
    @app.route('/guider/',methods=['GET'])
    @app.route('/guider.html',methods=['GET'])
    @login_required
    def guider():
        return render_template('guider.html')

    @app.route('/solver',methods=['GET'])
    @app.route('/solver/',methods=['GET'])
    @app.route('/solver.html',methods=['GET'])
    @login_required
    def solver():
        return render_template('solver.html')
        
    @app.route('/novnc',methods=['GET'])
    @app.route('/novnc/',methods=['GET'])
    @app.route('/novnc.html',methods=['GET'])
    @login_required
    def novnc():
        return render_template('novnc.html')

    @app.route('/client',methods=['GET'])
    @app.route('/client/',methods=['GET'])
    @app.route('/client.html',methods=['GET'])
    @login_required
    def client():
        return render_template('client.html')

    @app.route('/desktop',methods=['GET'])
    @app.route('/desktop/',methods=['GET'])
    @app.route('/desktop.html',methods=['GET'])
    @login_required
    def desktop():
        return render_template('desktop.html')

    @app.route('/ndesktop',methods=['GET'])
    @app.route('/ndesktop/',methods=['GET'])
    @app.route('/ndesktop.html',methods=['GET'])
    @login_required
    def ndesktop():
        return render_template('ndesktop.html')

    @app.route('/ndesktop-system',methods=['GET'])
    @app.route('/ndesktop-sysem/',methods=['GET'])
    @app.route('/ndesktop-system.html',methods=['GET'])
    @login_required
    def ndesktop_sysem():
        return render_template('ndesktop-system.html')

    @app.route('/ndesktop-browser',methods=['GET'])
    @app.route('/ndesktop-browser/',methods=['GET'])
    @app.route('/ndesktop-browser.html',methods=['GET'])
    @login_required
    def ndesktop_browser():
        return render_template('ndesktop-browser.html')

    @app.route('/ndesktop-store',methods=['GET'])
    @app.route('/ndesktop-store/',methods=['GET'])
    @app.route('/ndesktop-store.html',methods=['GET'])
    @login_required
    def ndesktop_store():
        return render_template('ndesktop-store.html')

    @app.route("/skymap",methods=['GET'])
    @app.route("/skymap/",methods=['GET'])
    @app.route("/skymap.html",methods=['GET'])
    @login_required
    def skymap():
        return render_template('skymap.html')

    @app.route("/scripteditor",methods=['GET'])
    @app.route("/scripteditor/",methods=['GET'])
    @app.route("/scripteditor.html",methods=['GET'])
    @login_required
    def scripteditor():
        return render_template('scripteditor.html')

    @app.route("/imageviewer",methods=['GET'])
    @app.route("/imageviewer/",methods=['GET'])
    @app.route("/imageviewer.html",methods=['GET'])
    @login_required
    def imageviewer():
        return render_template('imageviewer.html')

    @app.route("/search",methods=['GET'])
    @app.route("/search/",methods=['GET'])
    @app.route("/search.html",methods=['GET'])
    @login_required
    def search():
        return render_template('search.html')

    @app.route("/webssh" , methods=['GET'])
    @app.route("/webssh/", methods=['GET'])
    @app.route("/webssh.html", methods=['GET'])
    @login_required
    def webssh():
        return redirect("http://127.0.0.1:8888",code=301)

    @app.route("/tools" , methods=['GET'])
    @app.route("/tools/", methods=['GET'])
    @app.route("/tools.html", methods=['GET'])
    @login_required
    def tools():
        return render_template("tools.html")

    @app.route("/settings",methods=['GET'])
    @app.route("/settings/",methods=['GET'])
    @app.route("/settings.html",methods=['GET'])
    @login_required
    def settings():
        return render_template("settings.html")

    @app.route("/bugreport", methods=['GET'])
    @app.route("/bugreport/", methods=['GET'])
    @app.route("/bugreport.html", methods=['GET'])
    def bug_report():
        return render_template("bugreport.html")

    @app.route("/debug",methods=['GET'])
    @app.route("/debug/", methods=['GET'])
    @app.route("/debug.html", methods=['GET'])
    @login_required
    def debug():
        return render_template("debug.html")

    @app.errorhandler(403)
    def page_not_found(error):
        return render_template('error.html',error="403_FORBIDDEN_FORM_ERROR"), 403
        
    @app.errorhandler(404)
    def page_not_found(error):
        return render_template('error.html',error="404_PAGE_NOT_FOUND"), 404

    @app.errorhandler(500)
    def server_error(error):
        return render_template('error.html',error="500_INTERNET_SERVER_ERROR"), 500

from flask import Markup,Blueprint,current_app
import os

class _WebBasic(object):
    """
        Web Basic View interface
    """

    @staticmethod
    def load_basic_js():
        """
            Load Basic JavaScript files
            Includes the following files:
                adminlte.min.js
                jquery.min.js
                bootstrap.bunble.min.js
        """
        js = """
            <!-- jQuery -->
            <script src="/static/js/jquery/jquery.min.js"></script>
            <!-- Bootstrap 4 -->
            <script src="/static/js/bootstrap/bootstrap.bundle.min.js"></script>
            <!-- AdminLTE App -->
            <script src="/static/js/adminlte.min.js"></script>
        """
        return Markup(js)

    @staticmethod
    def load_basic_css():
        """
            Load basic CSS files
            Includes the following files:
                fontawesome.min.css
                adminlte.min.css
        """
        css = """
                <!-- Font Awesome -->
                <link rel="stylesheet" href="/static/css/fontawesome/fontawesome.min.css">
                <!-- Theme style -->
                <link rel="stylesheet" href="/static/css/adminlte.min.css">
            """
        return Markup(css)

class WebBasic(object):
    """
        Interfaces of the Web Basic
    """

    def __init__(self,app) -> None:
        """
            Construct a new Web Basic object
            Args :
                app : Flask application
            Returns : None
        """
        if app is not None:
            self.init_app(app)

    def init_app(self, app) -> None:
        """
            Initialize the Web Basic object and bind it to the application
            Args : 
                app : Flask application
            Returns : None
        """
        blueprint = Blueprint('basic', __name__,
                              static_folder=os.path.join(os.getcwd(),"client",'static'))
        app.register_blueprint(blueprint)

        if not hasattr(app, 'extensions'):
            app.extensions = {}
        app.extensions['basic'] = _WebBasic
        app.context_processor(self.context_processor)

    @staticmethod
    def context_processor():
        return {
            'basic': current_app.extensions['basic']
        }