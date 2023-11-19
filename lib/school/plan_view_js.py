import base64
import hashlib
import time
from urllib.parse import urlencode
import Crypto.Cipher
from Crypto.Util.Padding import pad


class PlanViewJs:
    def process_data(self, e):
        # 销毁 s.a 对象（假设在代码中有相关定义）
        # s.a.destroy()

        # 获取当前时间戳
        current_time = int(time.time() * 1000)

        # 构建需要发送的数据
        t = {
            'tj_id': e['tj_id'],
            'is_view': e['is_view'],
            'buy_view': e['buy_view'],
            'time': '666EOL' + str(current_time)[3:]
        }

        # 对数据进行处理（假设有 _.e 函数用于处理数据）
        #t = _.e({'obj': t})

        # 将数据转换为查询字符串
        query_string = urlencode(t)
        print(query_string)

        if e['is_view'] != 2:
            # 发送 GET 请求（假设有 b.q 函数用于发送请求）
            # response = requests.get(f'/school/{p}/tjcx/{t}')
            #response = requests.get(f'/school/{p}/tjcx/{query_string}')
            pass
        else:
            # 执行 T 函数（假设有 T 函数用于某些操作）
            # T(True)
            pass

    def r(e):
        def stringify(obj):
            keys = sorted(obj.keys())
            result = {}
            for key in keys:
                value = obj[key]
                if value is not None:
                    result[key] = str(value)
            return result

        n = stringify(e['obj'])
        a = ""
        for key, value in n.items():
            a += key + "=" + value + "&"
        a = a[:-1]

        o = hashlib.md5(b"BLRjQozGFgEPXntk").digest()
        iv = hashlib.md5(b"ulbDIymJrsB7jnzS").digest()
        cipher = AES.new(o, AES.MODE_CBC, iv)
        encrypted_data = cipher.encrypt(pad(a.encode(), AES.block_size))
        encrypted_data = base64.b64encode(encrypted_data).decode()

        return encrypted_data

if __name__ == '__main__':
    spider = PlanViewJs()
    # 调用函数，传入适当的参数
    e = {
        'tj_id': '56422',
        'is_view': 1,
        'buy_view': 2
    }
    spider.process_data(e)
    pass
