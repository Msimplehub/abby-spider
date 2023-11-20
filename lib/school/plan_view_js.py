import base64
import binascii
import hashlib
import time
from urllib.parse import urlencode
import Crypto.Cipher
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad


class PlanViewJs:
    def process_data(self, tj_id, is_view, buy_view):
        # 销毁 s.a 对象（假设在代码中有相关定义）
        # s.a.destroy()

        # 获取当前时间戳
        current_time = int(time.time() * 1000)

        # 构建需要发送的数据
        t = {
            'tj_id': tj_id,
            'is_view': is_view,
            'buy_view': buy_view,
            'time': '666EOL' + str(current_time)[3:]
        }

        # 对数据进行处理（假设有 _.e 函数用于处理数据）
        t = self.r({'obj': t})
        print(t)
        return t
        # 将数据转换为查询字符串
        #query_string = urlencode(t)
        #print(query_string)

        #if e['is_view'] != 2:
            # 发送 GET 请求（假设有 b.q 函数用于发送请求）
            # response = requests.get(f'/school/{p}/tjcx/{t}')
            #response = requests.get(f'/school/{p}/tjcx/{query_string}')
           # pass
        #else:
            # 执行 T 函数（假设有 T 函数用于某些操作）
            # T(True)
           # pass

    def r(self, e):
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
        o = b"BLRjQozGFgEPXntk"
        iv = b"ulbDIymJrsB7jnzS"
        cipher = AES.new(o, AES.MODE_CBC, iv)
        encrypted_data = cipher.encrypt(pad(a.encode(), AES.block_size, style='pkcs7'))
        encrypted_data = binascii.b2a_hex(encrypted_data).decode()

        return encrypted_data

if __name__ == '__main__':
    spider = PlanViewJs()
    # 调用函数，传入适当的参数
    e = {
        'tj_id': '57735',
        'is_view': 1,
        'buy_view': 2
    }
    spider.process_data(e["tj_id"], e["is_view"], e["buy_view"])
    pass
