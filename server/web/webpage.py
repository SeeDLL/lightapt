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

    @app.route("/imagecropper",methods=['GET'])
    @app.route("/imagecropper/",methods=['GET'])
    @app.route("/imagecropper.html",methods=['GET'])
    @login_required
    def imagecropper():
        return render_template('imagecropper.html')

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

    @app.route("/faq",methods=['GET'])
    @app.route("/faq/", methods=['GET'])
    @app.route("/faq.html", methods=['GET'])
    @login_required
    def faq():
        return render_template("faq.html")

    @app.route("/license",methods=['GET'])
    @app.route("/license/", methods=['GET'])
    @app.route("/license.html", methods=['GET'])
    def licenses():
        return render_template("license.html")

    @app.route("/calendar",methods=['GET'])
    @app.route("/calendar/", methods=['GET'])
    @app.route("/calendar.html", methods=['GET'])
    @login_required
    def calendar():
        return render_template("calendar.html")

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

    @app.route("/test",methods=['GET'])
    @app.route("/test/", methods=['GET'])
    @app.route("/test.html", methods=['GET'])
    @login_required
    def test():
        return render_template("test.html")

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
    def icon():
        """
            Load the icon file to display on the web templates
        """
        icon = '<link rel="icon" sizes="16x16" type="image/icon" href="/static/textures/icon.ico">'
        return Markup(icon)
        
    @staticmethod
    def load_basic_meta():
        """
            Load the basic metadata for the templates
        """
        meta = """
            <meta charset="utf-8">
            <meta http-equiv="X-UA-Compatible" content="IE=edge">
            <meta name="viewport" content="width=device-width, initial-scale=1">
        """
        return Markup(meta)

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

    @staticmethod
    def load_danger_model():
        """
            Add a new danger model to templates
            Args : None
            Returns : Markup object
        """
        model = """
            <!-- Modal container -->
            <div class="container">
                <!-- Central Modal Medium Danger -->
                <div class="modal fade" id="centralModalDanger" tabindex="-1" role="dialog" aria-labelledby="myModalLabel"
                    aria-hidden="true">
                    <div class="modal-dialog modal-notify modal-danger" role="document">
                        <!--Content-->
                        <div class="modal-content">
                            <!--Header-->
                            <div class="modal-header">
                                <p class="heading lead" id="errorModalTitle">错误信息</p>
                                <button type="button" class="close modal-voy-btn" data-dismiss="modal" aria-label="Close">
                                    <span aria-hidden="true" class="white-text">&times;</span>
                                </button>
                            </div>
                            <!--Body-->
                            <div class="modal-body">
                                <div class="text-center">
                                    <i class="fas fa-exclamation-triangle fa-4x mb-3 animated bounceIn"></i>
                                    <p id="errorMessage" class="note note-danger">
                                        未知错误
                                    </p>
                                    <p id="contactMessage" class="text-muted">
                                        <small>如果你有任何问题，请将详细细节告知开发者</small>
                                    </p>
                                </div>
                            </div>
                            <!--Footer-->
                            <div class="modal-footer justify-content-center">
                                <a class="btn btn-outline-danger modal-voy-btn"
                                    href="mailto:astro_air@126.com,fran.dibiase@gmail.com">
                                    <i class="fas fa-envelope mr-1"></i>联系我们</a>
                                <button type="button" class="btn btn-danger waves-effect modal-voy-btn" data-dismiss="modal">
                                    Ok
                                </button>
                            </div>
                        </div>
                        <!--/.Content-->
                    </div>
                </div>
            </div>
            <!-- Modal container end -->
        """
        return Markup(model)

    @staticmethod
    def load_warning_model():
        """
            Add a warning model to templates
        """
        model = """
            <div class="container">
                <!-- Central Modal Medium Warning -->
                <div class="modal fade" id="modalDoubleWarning" tabindex="-1" role="dialog" aria-labelledby="myModalLabel"
                    aria-hidden="true">
                    <div class="modal-dialog modal-notify modal-warning modal-lg" role="document">
                        <!--Content-->
                        <div class="modal-content">
                            <!--Header-->
                            <div class="modal-header">
                                <p class="heading lead" id="modalWarnTit">确认操作?</p>
                                <button type="button" class="close" data-dismiss="modal" aria-label="Close">
                                    <span aria-hidden="true" class="white-text">&times;</span>
                                </button>
                            </div>
                            <!--Body-->
                            <div class="modal-body">
                                <div class="text-center">
                                    <i class="fas fa-question fa-4x mb-3 animated rotateIn text-danger"></i>
                                    <p id="contWarnModal" class="text-warning"></p>
                                    <p>你确定要执行这步操作吗?</p>
                                </div>
                            </div>
                            <!--Footer-->
                            <div class="modal-footer justify-content-center">
                                <div class="row">
                                    <div class="col-sm-6">
                                        <a type="button" id="confirmDoubleWarn" class="btn btn-sm btn-warning btn-block">
                                            确认
                                            <i class="fas fa-check"></i>
                                        </a>
                                    </div>
                                    <div class="col-sm-6">
                                        <a type="button" class="btn btn-sm btn-outline-warning waves-effect btn-block"
                                            data-dismiss="modal">
                                            Nope
                                        </a>
                                    </div>
                                </div>
                            </div>
                        </div>
                        <!--/.Content-->
                    </div>
                </div>
                <!-- Central Modal Medium Warning-->
            </div>
        """
        return Markup(model)

    @staticmethod
    def load_info_model():
        """
            Add a info model to templates
        """
        model = """
            <!-- Container Modal -->
            <div class="container">
                <!-- Central Modal Medium Generic info -->
                <div class="modal fade" id="infoModalGeneric" tabindex="-1" role="dialog" aria-labelledby="myModalLabel2"
                    aria-hidden="true">
                    <div class="modal-dialog modal-notify modal-info" role="document">
                        <!--Content-->
                        <div class="modal-content">
                            <!--Header-->
                            <div class="modal-header">
                                <p class="heading lead">信息</p>
                                <button type="button" id="closeModalInfo" class="close modal-voy-btn" data-dismiss="modal"
                                    aria-label="Close">
                                    <span aria-hidden="true" class="white-text">&times;</span>
                                </button>
                            </div>

                            <!--Body-->
                            <div class="modal-body">
                                <div class="text-center">
                                    <div class="spinner-border text-primary m-5" role="status">
                                        <span class="sr-only">常规信息</span>
                                    </div>
                                    <p id="infoModalMessage" class="note note-info">
                                        常规消息...
                                    </p>
                                    <p id="genericMessageinfo" class="text-muted">
                                        <small></small>
                                    </p>
                                </div>
                            </div>
                            <!--Footer-->
                            <div class="modal-footer justify-content-center">
                                <button type="button" class="btn btn-primary modal-voy-btn" data-dismiss="modal">
                                    Ok
                                </button>
                            </div>
                        </div>
                        <!--/.Content-->
                    </div>
                </div>
                <!-- Central Modal Medium Danger-->
            </div>
            <!-- Container Modal end -->
        """
        return Markup(model)

    @staticmethod
    def loading():
        """
            Add a loading animation to the template
        """
        loading = """
            <!-- loading开始 -->
            <div id="loading-animation">
                <div id="loading-animation-center">
                    <div id="loading-animation-center-absolute">
                        <div class="loading_object" id="loading_four"></div>
                        <div class="loading_object" id="loading_three"></div>
                        <div class="loading_object" id="loading_two"></div>
                        <div class="loading_object" id="loading_one"></div>
                    </div>
                </div>
            </div>
            <script>!function () { function e() { setTimeout(() => { $("#loading-animation").fadeOut(540) }, 500) } window.jQuery ? $(document).ready(() => { e() }) : document.onreadystatechange = (() => { "interactive" === document.readyState && e() }) }();</script>
            <!-- loading 结束 -->
        """
        return Markup(loading)

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