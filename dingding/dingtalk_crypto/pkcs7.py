# -*- coding: utf-8 -*-

import binascii
import StringIO


class PKCS7(object):
    """
    RFC 2315: PKCS#7 page 21
    有些加密算法需要加密的数据的长度必需是8的倍数
    """
    def __init__(self, k=16):
        self.k = k

    def decode(self, text):
        """
        删除 PKCS#7 方式填充的字符串
        :param text: str
        :return: str
        """
        n1 = len(text)
        val = int(binascii.hexlify(text[-1]), 16)
        if val > self.k:
            raise ValueError("Input is not padded or padding is corrupt")
        l = n1 - val
        return text[:l]

    def encode(self, text):
        """
        安装 PKCS#7 标准填充字符串
        :param text: str
        :return: str
        """
        l = len(text)
        output = StringIO.StringIO()
        val = self.k - (l % self.k)
        for _ in xrange(val):
            output.write('%02x' % val)
        return text + binascii.unhexlify(output.getvalue())