from pymongo import MongoClient
from datetime import datetime

class function:
    # 初始化函数
    def __init__(self):
        db_name="blog"
        self.collection_userinfo = "userinfo"
        self.collection_postinfo = "postinfo"
        self.collection_commentsinfo="commentsinfo"
        client=MongoClient("mongodb://127.0.0.1:27017")
        self.database=client[db_name]
        db_list=client.list_database_names()
        print("checking mongodb connection")
        print("-------------------------------------------")
        if db_name in db_list:
            print("{} exit".format(db_name))
            print("-------------------------------------------")
        else:
            print("database {} is not exit.".format(db_name))
            print("-------------------------------------------")
            print("creating database")
        col_list=self.database.list_collection_names()
        if self.collection_userinfo in col_list:
            print("collection {} exit".format(self.collection_userinfo))
        elif self.collection_postinfo in col_list:
            print("collection {} exit".format(self.collection_postinfo))
            print("-------------------------------------------")
        else:
            print("collection {} is not exit".format(self.collection_postinfo))
            print("-------------------------------------------")
            print("creating collections")
            self.database.get_collection(self.collection_postinfo).insert_one({"post_id":"test","user_id":"test","post_time":"test","title":"test","content":"test","type":"test","is_delete":1})
            self.database.get_collection(self.collection_userinfo).insert_one({"user_id": "test", "username": "test", "passwd": "test", "phone": "test", "e_mail": "test","create_time": "test"})
            self.database.get_collection("counters").insert_one({"_id":"user_id","sequence_value":0})
            self.database.get_collection("counters").insert_one({"_id": "post_id", "sequence_value": 1})
            print("-------------------------------------------")
            print("create success!")

    # 定义post写入mongodb的函数，插入成功则返回TRUE，失败返回FALSE
    def write_post(self, title, content, post_type,post_user):
        b=False
        # post_user="superuser"
        # 通过datetime获取写入时间,格式化为：2002-4-4 12:12:12格式
        post_time=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        # 从id集合中获取id值
        post_id=self.get_next_id(id_type="post")[0]["sequence_value"]
        print(post_id,type(post_id))
        # 从user集合中通过username获取user_id一起写入post集合中
        user_id=self.database.get_collection(self.collection_userinfo).find({"username":post_user},{"_id":0,"user_id":1})[0]["user_id"]
        result=self.database.get_collection(self.collection_postinfo).insert_one({"post_id":post_id,"user_id":user_id,"post_time":post_time,"title":title,"content":content,"type":post_type,"is_delete":0})
        if result.inserted_id != "":
            b=True
        return b

    # 定义修改帖子的方法，实现方法与write_post基本一致，插入改为更新
    def edit(self,post_id,title,content,post_type,post_user):
        b=False
        # post_user="superuser"
        post_time=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        user_id=self.database.get_collection(self.collection_userinfo).find({"username":post_user},{"_id":0,"user_id":1})[0]["user_id"]
        result=self.database.get_collection(self.collection_postinfo).update_one({"post_id":post_id},{"$set":{"user_id":user_id,"post_time":post_time,"title":title,"content":content,"type":post_type,"is_delete":0}})
        if result.acknowledged:
            b=True
        return b

    # 定义写入评论的方法
    def write_comment(self,post_id,comment,username):
        b=False
        result=self.database.get_collection(self.collection_commentsinfo).insert_one({"post_id":post_id,"comment":comment,"username":username,"is_delete":0})
        if result.inserted_id !="":
            b=True
        return b

    # 获取评论的方法,通过post_id获取
    def get_comment(self,post_id):
        result=self.database.get_collection(self.collection_commentsinfo).find({"post_id":str(post_id)+".0"},{"_id":0,"comment":1,"username":1})
        return result

    # get post 方法
    # 通过post类型查询帖子
    def get_post_by_type(self,post_type):
        if post_type=="all":
            result=self.database.get_collection(self.collection_postinfo).find({"is_delete":0},{"_id":0,"title":1,"post_time":1,"content":1,"post_id":1})
        else:
            result=self.database.get_collection(self.collection_postinfo).find({"type":post_type,"is_delete":0},{"_id":0,"title":1,"post_time":1,"content":1,"post_id":1})
        return result

    # 通过post的id查询帖子
    def get_post_by_id(self,post_id):
        result=self.database.get_collection(self.collection_postinfo).find({"post_id":post_id,"is_delete":0},{"_id":0,"title":1,"post_time":1,"content":1,"post_id":1})
        return result

    # 通过发布帖子的用户username查询帖子
    def get_post_by_username(self,username):
        user_id=self.database.get_collection(self.collection_userinfo).find({"username":username},{"_id":0,"user_id":1})[0]["user_id"]
        result=self.database.get_collection(self.collection_postinfo).find({"user_id":user_id,"is_delete":0},{"_id":0,"title":1,"post_time":1,"content":1,"post_id":1})
        return result

    # 定义新建用户的方法返回一个Boolean值和message信息判断是否注册成功
    def create_user(self,username,passwd,phone,e_mail):
        b=False
        # 通过在userinfo集合中查询username判断该用户名是否被占用
        query_username=self.database.get_collection(self.collection_userinfo).find({"username":username})
        query_username=list(query_username)
        if len(query_username)>0:
            massage="用户名已存在"
            return b,massage
        else:
            massage="注册失败"
            create_time=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            user_id=self.get_next_id(id_type="user")[0]["sequence_value"]
            result=self.database.get_collection(self.collection_userinfo).insert_one({"user_id":user_id,"username":username,"passwd":passwd,"phone":phone,"e_mail":e_mail,"create_time":create_time})
            if result.inserted_id != "":
                b = True
                massage="注册成功!"
            return b,massage

    # 实现用户登录功能
    def user_login(self,username,passwd):
        b=False
        result=self.database.get_collection(self.collection_userinfo).find({"username":username},{"_id":0,"passwd":1})
        if result is not None:
            if list(result)[0]["passwd"]==passwd:
                b=True
            return b
        return b

    # 更新写入的userid或postid，返回id值
    def get_next_id(self,id_type):
        collection_counter=self.database["counters"]
        if id_type=="user":
            query={"_id":"user_id"}
            update={"$inc":{"sequence_value":1}}
            collection_counter.update_one(query,update)
        elif id_type=="post":
            query={"_id":"post_id"}
            update={"$inc":{"sequence_value":2}}
            collection_counter.update_one(query,update)
        return collection_counter.find({"_id":id_type+"_id"},{"sequence_value":1})

    # 删除帖子的方法实现，修改帖子的is_delete字段为1表示删除
    def delete_post(self,post_id):
        message="已删除"
        result=self.database.get_collection(self.collection_postinfo).update_one({"post_id":post_id},{"$set":{"is_delete":1}})
        if result.acknowledged:
            return message
        else:
            message="删除失败，请重新尝试"
            return message





