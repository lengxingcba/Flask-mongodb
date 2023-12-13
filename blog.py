from flask import Flask, render_template, request, url_for, flash, redirect, make_response
from mongodb_functions import function

# render_template方法和redirect方法用于页面直接的跳转和信息的传递。
# flash为显示提示语的实现。

function = function()
app = Flask(__name__)
app.secret_key = "MrFreeGiving"

# 定义登录的路由地址和方法
@app.route("/login", methods=("GET", "POST"))
def Login():
    username = request.form["username"]
    passwd = request.form["passwd"]
    result = function.user_login(username, passwd)
    if result:
        flash("欢迎你，{}".format(username))
        # 通过设置cookie缓存来保存登录的用户信息用于各个页面的用户信息获取
        resp = make_response(redirect("/"))
        resp.set_cookie("username", username)
        return resp
    else:
        flash("用户不存在")
        return render_template("Login.html")

# 定义登出的路由地址和方法
@app.route("/logout", methods=("POST",))
def logout():
    resp = make_response(redirect("/"))
    resp.delete_cookie('username')
    return resp

# 用户注册
@app.route("/register", methods=("GET", "POST"))
def user_register():
    return render_template("register.html")

# 用户中心
@app.route("/user_center", methods=("GET", "POST"))
def user_center():
    username = request.cookies.get("username")
    if username is None:
        return render_template("Login.html")
    else:
        user_posts = list(function.get_post_by_username(username))
        return render_template("user_center.html", username=username, posts=user_posts)

# 主页面
@app.route("/")
def index():
    username = request.cookies.get("username") if request.cookies.get("username") is not None else "请登录"
    post_type = request.args.get("name")
    print(post_type)
    posts = function.get_post_by_type(post_type=post_type)
    posts = list(posts)
    for post in posts:
        print(type(post))
        print(post["title"])
    return render_template("index.html", posts=posts, username=username)

# 新建文章页面
@app.route("/new", methods=("GET", "POST"))
def new():
    post_user = request.cookies.get("username")
    if request.method == "POST":
        title = request.form["self"]
        content = request.form["content"]
        post_type = request.form["selectList"]
        print(post_type)
        print(title, type(title))
        print(content, type(content))
        if post_user is not None:
            if not title:
                flash("请输入标题")
            elif not content:
                flash("内容不能为空")
            else:
                result = function.write_post(title, content, post_type=post_type, post_user=post_user)
                if result:
                    flash("保存成功!")
                    return redirect(url_for("index"))
                else:
                    flash("保存失败，请重新提交")
            return render_template("new.html", username=post_user)
        else:
            flash("只有登录才能发布")
            return render_template("Login.html")
    return render_template("new.html", username=post_user)


@app.route("/edit", methods=("GET", "POST"))
def to_edit():
    post_id=request.args.get("post_id")
    post=function.get_post_by_id(int(post_id[:-2]))[0]
    return render_template("edit.html",post=post)

@app.route("/edit/<int:post_id>",methods=("GET", "POST"))
def edit():
    post_user = request.cookies.get("username")
    if request.method == "POST":
        title = request.form["title"]
        content = request.form["content"]
        post_type = request.form["selectList"]
        post_id=request.form["post_id"]
        print(post_type)
        print(title, type(title))
        print(content, type(content))
        if post_user is not None:
            if not title:
                flash("请输入标题")
            elif not content:
                flash("内容不能为空")
            else:
                result = function.edit(int(post_id[-2]),title, content, post_type=post_type, post_user=post_user)
                if result:
                    flash("保存成功!")
                    return redirect(url_for("user_center"))
                else:
                    flash("保存失败，请重新提交")
            return render_template("edit.html", username=post_user)
    return render_template("user_center.html", username=post_user)


# 帖子详细页面
@app.route("/posts/<int:post_id>")
def post(post_id):
    username = request.cookies.get("username")
    result = function.get_post_by_id(post_id=post_id)
    result = list(result)[0]
    print(result)
    comments = list(function.get_comment(post_id=post_id))
    for comment in comments:
        print(comment)
    return render_template("post.html", post=result, comments=comments, username=username)

# 删除业务
@app.route("/posts/<int:post_id>/delete", methods=("POST",))
def delete(post_id):
    post = function.get_post_by_id(post_id)
    message = function.delete_post(post_id=post_id)
    flash(message)
    return redirect(url_for("user_center"))

# 注册业务
@app.route("/user_register", methods=("POST",))
def register():
    if request.method == "POST":
        username = request.form["username"]
        passwd = request.form["passwd"]
        e_mail = request.form["e_mail"]
        phone = request.form["phone"]
        print(username)
        b, message = function.create_user(username=username, passwd=passwd, e_mail=e_mail, phone=phone)
        print(b, message)
        if b:
            flash(message)
            return redirect(url_for("index", username=username))
        else:
            flash(message)
            return render_template("register.html")
    else:
        return render_template("register.html")

# 添加评论业务
@app.route("/add_comment", methods=("POST",))
def add_comment():
    username = request.cookies.get("username")
    comment = request.form["comment"]
    post_id = request.form["post_id"]
    result = function.write_comment(post_id, comment, username)
    if result:
        flash("添加评论成功！")


    else:
        flash("添加评论失败")
    return redirect("/")


while True:
    app.run(debug=True)
