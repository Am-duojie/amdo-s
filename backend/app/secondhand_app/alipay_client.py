"""
支付宝支付接口集成
文档：https://opendocs.alipay.com/common/02kkv7
"""
import json
import hashlib
import base64
from datetime import datetime
from Crypto.PublicKey import RSA
from Crypto.Signature import pkcs1_15
from Crypto.Hash import SHA256
from django.conf import settings
import logging
import requests
from urllib.parse import quote

logger = logging.getLogger(__name__)


class AlipayClient:
    """支付宝支付客户端"""
    
    def __init__(self):
        # 从settings中读取配置
        self.app_id = getattr(settings, 'ALIPAY_APP_ID', '')
        self.app_private_key = getattr(settings, 'ALIPAY_APP_PRIVATE_KEY', '')
        self.alipay_public_key = getattr(settings, 'ALIPAY_PUBLIC_KEY', '')
        self.gateway_url = getattr(settings, 'ALIPAY_GATEWAY_URL', 'https://openapi.alipay.com/gateway.do')
        self.charset = 'utf-8'
        self.sign_type = 'RSA2'
        self.version = '1.0'
    
    def validate_config(self):
        """
        验证配置是否完整
        参考：https://opendocs.alipay.com/common/02kkv7
        """
        errors = []
        
        if not self.app_id:
            errors.append('支付宝APPID未配置，请在 settings.py 中配置 ALIPAY_APP_ID')
        elif len(self.app_id) < 10:
            errors.append(f'支付宝APPID格式可能不正确: {self.app_id}')
        
        if not self.app_private_key:
            errors.append('支付宝应用私钥未配置，请在 settings.py 中配置 ALIPAY_APP_PRIVATE_KEY')
        else:
            # 验证私钥格式
            try:
                private_key_str = self._format_private_key(self.app_private_key)
                if not private_key_str:
                    errors.append('应用私钥格式错误，无法解析')
                else:
                    private_key = RSA.import_key(private_key_str)
                    if private_key.size_in_bits() != 2048:
                        errors.append(f'应用私钥长度不正确，应为2048位，当前为{private_key.size_in_bits()}位')
            except Exception as e:
                errors.append(f'应用私钥验证失败: {str(e)}')
        
        if not self.alipay_public_key:
            errors.append('支付宝公钥未配置，请在 settings.py 中配置 ALIPAY_PUBLIC_KEY')
        else:
            # 验证公钥格式
            try:
                public_key_str = self._format_public_key(self.alipay_public_key)
                if not public_key_str:
                    errors.append('支付宝公钥格式错误，无法解析')
                else:
                    public_key = RSA.import_key(public_key_str)
                    if public_key.size_in_bits() != 2048:
                        errors.append(f'支付宝公钥长度不正确，应为2048位，当前为{public_key.size_in_bits()}位')
            except Exception as e:
                errors.append(f'支付宝公钥验证失败: {str(e)}')
        
        if errors:
            return False, '; '.join(errors)
        
        return True, ''
    
    def _format_private_key(self, key_str):
        """格式化私钥字符串"""
        if not key_str:
            return None
        # 移除可能的头尾标记和换行符
        key_str = key_str.replace('-----BEGIN RSA PRIVATE KEY-----', '')
        key_str = key_str.replace('-----END RSA PRIVATE KEY-----', '')
        key_str = key_str.replace('-----BEGIN PRIVATE KEY-----', '')
        key_str = key_str.replace('-----END PRIVATE KEY-----', '')
        key_str = key_str.replace('\n', '').replace('\r', '').replace(' ', '')
        # 添加标准头尾
        formatted_key = f"-----BEGIN RSA PRIVATE KEY-----\n"
        # 每64个字符换行
        for i in range(0, len(key_str), 64):
            formatted_key += key_str[i:i+64] + '\n'
        formatted_key += "-----END RSA PRIVATE KEY-----"
        return formatted_key
    
    def _format_public_key(self, key_str):
        """格式化公钥字符串"""
        if not key_str:
            return None
        # 移除可能的头尾标记和换行符
        key_str = key_str.replace('-----BEGIN PUBLIC KEY-----', '')
        key_str = key_str.replace('-----END PUBLIC KEY-----', '')
        key_str = key_str.replace('\n', '').replace('\r', '').replace(' ', '')
        # 添加标准头尾
        formatted_key = f"-----BEGIN PUBLIC KEY-----\n"
        # 每64个字符换行
        for i in range(0, len(key_str), 64):
            formatted_key += key_str[i:i+64] + '\n'
        formatted_key += "-----END PUBLIC KEY-----"
        return formatted_key
    
    def _sign(self, data):
        """
        使用RSA2签名
        严格按照支付宝官方文档规范：https://opendocs.alipay.com/common/02kipl
        """
        try:
            # 格式化私钥
            private_key_str = self._format_private_key(self.app_private_key)
            if not private_key_str:
                raise ValueError('私钥格式错误')
            
            # 加载私钥
            private_key = RSA.import_key(private_key_str)
            
            # 支付宝签名规范：
            # 1. 筛选并排序：获取所有请求参数，除去sign、sign_type两个参数外，其他参数都要参与签名
            # 2. 排序：按照参数名ASCII码从小到大排序（字典序）
            # 3. 拼接：将排序后的参数与其对应值，组合成"参数=参数值"的格式，并且把这些参数用&字符连接起来
            # 4. 签名：使用RSA2算法，对拼接后的字符串进行签名
            
            filtered_data = {}
            for k, v in data.items():
                # 只排除 sign 参数（不参与签名）
                # sign_type 需要参与签名（支付宝官方文档要求）
                if k == 'sign':
                    continue
                # 排除空值（None、空字符串）
                if v is None or v == '':
                    continue
                # 保留所有非空值
                filtered_data[k] = str(v)  # 确保所有值都是字符串
            
            # 按参数名ASCII码排序（字典序）
            sorted_data = sorted(filtered_data.items())
            
            # 构建签名字符串：key1=value1&key2=value2
            # 注意：参数值使用原始值，不进行URL编码（支付宝官方规范）
            sign_str = '&'.join([f'{k}={v}' for k, v in sorted_data])
            
            logger.info(f'========== 签名计算 ==========')
            logger.info(f'参与签名的参数数量: {len(sorted_data)}')
            logger.info(f'签名原文（完整）: {sign_str}')
            logger.info(f'签名原文长度: {len(sign_str)}')
            # 打印每个参数用于调试
            for k, v in sorted_data:
                logger.info(f'  参数: {k} = {v[:100] if len(str(v)) > 100 else v}')
            
            # 使用SHA256计算哈希值
            hash_obj = SHA256.new(sign_str.encode('utf-8'))
            
            # 使用私钥进行RSA2签名
            signer = pkcs1_15.new(private_key)
            signature = signer.sign(hash_obj)
            
            # Base64编码签名结果
            sign = base64.b64encode(signature).decode('utf-8')
            
            logger.info(f'签名结果（前50字符）: {sign[:50]}...')
            logger.info(f'签名结果长度: {len(sign)}')
            
            return sign
        except Exception as e:
            logger.error(f'签名失败: {str(e)}', exc_info=True)
            raise
    
    def _verify_sign(self, data, sign):
        """验证签名"""
        try:
            # 格式化公钥
            public_key_str = self._format_public_key(self.alipay_public_key)
            if not public_key_str:
                return False
            
            # 加载公钥
            public_key = RSA.import_key(public_key_str)
            
            # 对数据进行排序并拼接（支付宝规范：过滤空值、sign和sign_type参数，按参数名ASCII码排序）
            filtered_data = {}
            for k, v in data.items():
                # 排除 sign 和 sign_type
                if k in ['sign', 'sign_type']:
                    continue
                # 排除空值
                if v is None or v == '':
                    continue
                # 保留所有非空值
                filtered_data[k] = v
            
            # 按参数名ASCII码排序
            sorted_data = sorted(filtered_data.items())
            # 参数值使用原始值，不进行URL编码（支付宝规范）
            sign_str = '&'.join([f'{k}={v}' for k, v in sorted_data])
            
            logger.info(f'========== 签名验证 ==========')
            logger.info(f'验证签名原文: {sign_str}')
            logger.info(f'验证签名原文长度: {len(sign_str)}')
            
            # 计算SHA256哈希
            hash_obj = SHA256.new(sign_str.encode('utf-8'))
            
            # Base64解码签名
            signature = base64.b64decode(sign.encode('utf-8'))
            
            # 验证签名
            verifier = pkcs1_15.new(public_key)
            verifier.verify(hash_obj, signature)
            
            logger.info('签名验证成功')
            return True
        except Exception as e:
            logger.error(f'签名验证失败: {str(e)}', exc_info=True)
            return False
    
    def create_trade(self, out_trade_no, subject, total_amount, return_url=None, notify_url=None, **kwargs):
        """
        创建交易订单（电脑网站支付）
        接口：alipay.trade.page.pay
        官方文档：https://opendocs.alipay.com/apis/api_1/alipay.trade.page.pay
        
        参数说明：
        - out_trade_no: 商户订单号，商户网站订单系统中唯一订单号
        - subject: 订单标题
        - total_amount: 订单总金额，单位为元，精确到小数点后两位
        - return_url: 支付成功后跳转的页面（可选）
        - notify_url: 支付结果异步通知地址（可选）
        
        注意：
        1. return_url 和 notify_url 应该作为顶级参数，而不是放在 biz_content 中
        2. biz_content 必须是JSON字符串格式
        3. 所有参数值在签名时使用原始值，URL编码只在构建URL时进行
        """
        # 构建业务参数（biz_content）
        # 根据支付宝官方文档，biz_content 是JSON字符串格式
        biz_content = {
            'out_trade_no': str(out_trade_no),  # 商户订单号
            'product_code': 'FAST_INSTANT_TRADE_PAY',  # 产品码，固定值
            'total_amount': f'{float(total_amount):.2f}',  # 订单总金额，保留两位小数
            'subject': str(subject)[:256],  # 订单标题，最长256字符
        }
        
        # 添加其他业务参数（如果有）
        biz_content.update(kwargs)
        
        # 构建请求参数（按照支付宝官方文档规范）
        # 参考：https://opendocs.alipay.com/common/02kkv7
        params = {
            'app_id': self.app_id,  # 应用ID
            'method': 'alipay.trade.page.pay',  # 接口名称
            'charset': self.charset,  # 请求使用的编码格式，如utf-8
            'sign_type': self.sign_type,  # 签名类型，RSA2
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),  # 时间戳
            'version': self.version,  # 调用的接口版本，固定为1.0
            'biz_content': json.dumps(biz_content, ensure_ascii=False, separators=(',', ':')),  # 业务参数，JSON字符串格式（不使用ASCII转义，保持中文字符原样）
        }
        
        # return_url 和 notify_url 作为顶级参数（不在 biz_content 中）
        # 根据支付宝官方文档，这两个参数应该放在请求参数的顶层
        if return_url:
            params['return_url'] = str(return_url)
        if notify_url:
            # 确保notify_url没有被意外编码或包含非法字符
            params['notify_url'] = str(notify_url)
        
        # 生成签名
        # 支付宝签名要求：所有参数参与签名，除了sign和sign_type
        # 关键点：签名时的字符串必须与发送给支付宝的字符串完全一致（未URL编码前）
        params['sign'] = self._sign(params)
        
        logger.info(f'========== 支付宝支付请求 ==========')
        logger.info(f'接口URL: {self.gateway_url}')
        logger.info(f'APPID: {self.app_id}')
        logger.info(f'订单号: {out_trade_no}')
        logger.info(f'金额: {total_amount}')
        logger.info(f'商品标题: {subject}')
        logger.info(f'return_url: {return_url}')
        logger.info(f'notify_url: {notify_url}')
        logger.info(f'完整参数: {params}')
        
        # 构建完整URL（GET方式，需要URL编码）
        # 注意：签名时使用的是原始值（未编码），URL编码只在构建URL时进行
        # 支付宝官方文档要求：参数值需要进行URL编码，空格编码为%20
        # 按参数名排序（与签名时一致，确保URL参数顺序与签名时一致）
        sorted_params = sorted(params.items())
        # 手动构建查询字符串，使用quote进行编码
        # quote函数默认将空格编码为%20，符合支付宝要求
        query_parts = []
        for k, v in sorted_params:
            if v is not None:  # 过滤None值
                # 参数名和参数值都需要URL编码
                # safe='' 表示不保留任何特殊字符，全部编码
                encoded_key = quote(str(k), safe='')
                encoded_value = quote(str(v), safe='')
                query_parts.append(f'{encoded_key}={encoded_value}')
        query_string = '&'.join(query_parts)
        payment_url = f'{self.gateway_url}?{query_string}'
        
        logger.info(f'支付URL长度: {len(payment_url)} 字符')
        logger.debug(f'支付URL: {payment_url[:500]}...')  # 只打印前500个字符
        
        return {
            'success': True,
            'payment_url': payment_url,
            'params': params
        }
    
    def query_trade(self, out_trade_no):
        """
        查询交易订单
        接口：alipay.trade.query
        """
        # 构建业务参数
        biz_content = {
            'out_trade_no': str(out_trade_no),
        }
        
        # 构建请求参数
        params = {
            'app_id': self.app_id,
            'method': 'alipay.trade.query',
            'charset': self.charset,
            'sign_type': self.sign_type,
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'version': self.version,
            'biz_content': json.dumps(biz_content, ensure_ascii=True),
        }
        
        # 生成签名
        params['sign'] = self._sign(params)
        
        try:
            response = requests.post(self.gateway_url, data=params, timeout=10)
            result = response.json()
            
            logger.info(f'查询订单结果: {result}')
            
            # 解析响应
            response_data = result.get('alipay_trade_query_response', {})
            
            if response_data.get('code') == '10000':
                # 查询成功
                trade_status = response_data.get('trade_status', '')
                return {
                    'success': True,
                    'code': '10000',
                    'trade_status': trade_status,
                    'trade_no': response_data.get('trade_no', ''),
                    'out_trade_no': response_data.get('out_trade_no', ''),
                    'total_amount': response_data.get('total_amount', '0'),
                    'buyer_logon_id': response_data.get('buyer_logon_id', ''),
                }
            else:
                return {
                    'success': False,
                    'code': response_data.get('code', ''),
                    'msg': response_data.get('msg', '查询失败'),
                }
        except Exception as e:
            logger.error(f'查询订单异常: {str(e)}')
            return {
                'success': False,
                'msg': f'查询失败: {str(e)}'
            }
    
    def verify_notify(self, params):
        """验证支付通知签名"""
        sign = params.get('sign', '')
        if not sign:
            return False
        
        # 移除sign和sign_type参数
        verify_params = {k: v for k, v in params.items() if k not in ['sign', 'sign_type']}
        
        return self._verify_sign(verify_params, sign)

