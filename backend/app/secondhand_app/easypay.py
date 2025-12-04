"""
易支付接口集成
支付平台：https://pay.myzfw.com/
文档：https://pay.myzfw.com/doc_old.html
"""
import hashlib
import requests
from django.conf import settings
import logging

logger = logging.getLogger(__name__)


class EasyPayClient:
    """易支付客户端"""
    
    def __init__(self):
        # 从settings中读取配置
        self.submit_url = getattr(settings, 'EASYPAY_SUBMIT_URL', 'https://pay.myzfw.com/submit.php')
        self.mapi_url = getattr(settings, 'EASYPAY_MAPI_URL', 'https://pay.myzfw.com/mapi.php')
        self.api_url = getattr(settings, 'EASYPAY_API_URL', 'https://pay.myzfw.com/api.php')
        self.pid = getattr(settings, 'EASYPAY_PID', '')
        self.key = getattr(settings, 'EASYPAY_KEY', '')
        self.notify_url = getattr(settings, 'EASYPAY_NOTIFY_URL', '')
        self.return_url = getattr(settings, 'EASYPAY_RETURN_URL', '')
        self.demo_mode = getattr(settings, 'EASYPAY_DEMO_MODE', False)
    
    def validate_config(self):
        """验证配置是否完整"""
        if not self.pid or not self.key:
            return False, '支付功能未配置，请在 settings.py 中配置 EASYPAY_PID 和 EASYPAY_KEY'
        return True, ''
    
    def generate_sign(self, params):
        """
        生成MD5签名（易支付规范）
        1. 过滤空值和sign、sign_type参数
        2. 按参数名ASCII码排序
        3. 拼接成 key1=value1&key2=value2 格式
        4. 末尾拼接商户密钥
        5. MD5加密（小写）
        """
        # 过滤空值、sign、sign_type
        filtered = {
            k: str(v) for k, v in params.items() 
            if v is not None and v != '' and k not in ['sign', 'sign_type']
        }
        
        # 按键名ASCII码排序
        sorted_params = sorted(filtered.items(), key=lambda x: x[0])
        
        # 拼接成字符串
        sign_str = '&'.join([f'{k}={v}' for k, v in sorted_params])
        
        # 拼接密钥
        sign_str += self.key
        
        logger.info(f'签名原文: {sign_str}')
        
        # MD5加密（小写）
        sign = hashlib.md5(sign_str.encode('utf-8')).hexdigest().lower()
        
        return sign
    
    def verify_sign(self, params):
        """验证签名"""
        received_sign = params.get('sign', '')
        calculated_sign = self.generate_sign(params)
        return received_sign.lower() == calculated_sign.lower()
    
    def create_payment(self, order_id, order_name, amount, pay_type='alipay', return_url=None, notify_url=None, param=''):
        """
        创建支付订单（页面跳转支付）
        返回支付URL，前端直接跳转
        """
        params = {
            'pid': self.pid,
            'type': pay_type,
            'out_trade_no': str(order_id),
            'notify_url': notify_url or self.notify_url,
            'return_url': return_url or self.return_url,
            'name': order_name,
            'money': f'{float(amount):.2f}',
            'param': param,
            'sign_type': 'MD5',
        }
        
        # 生成签名
        params['sign'] = self.generate_sign(params)
        
        # 拼接URL
        query_string = '&'.join([f'{k}={v}' for k, v in params.items()])
        payment_url = f'{self.submit_url}?{query_string}'
        
        logger.info(f'创建支付URL: {payment_url}')
        
        return payment_url
    
    def create_payment_api(self, order_id, order_name, amount, client_ip, pay_type='alipay', notify_url=None, return_url=None, param='', device='pc'):
        """
        创建支付订单（API接口）
        返回支付二维码或跳转URL
        """
        # 演示模式
        if self.demo_mode:
            logger.info(f'========== 演示模式 ==========')
            logger.info(f'订单号: {order_id}, 金额: {amount}, 支付方式: {pay_type}')
            return {
                'code': 1,
                'msg': '演示模式：创建订单成功',
                'qrcode': 'https://api.qrserver.com/v1/create-qr-code/?size=300x300&data=https://example.com/demo-pay',
                'payurl': f'https://example.com/demo-pay?order={order_id}',
                'trade_no': f'DEMO_{order_id}',
            }
        
        params = {
            'pid': self.pid,
            'type': pay_type,
            'out_trade_no': str(order_id),
            'notify_url': notify_url or self.notify_url,
            'return_url': return_url or self.return_url,
            'name': order_name,
            'money': f'{float(amount):.2f}',
            'clientip': client_ip,
            'device': device,
            'param': param,
            'sign_type': 'MD5',
        }
        
        # 生成签名
        params['sign'] = self.generate_sign(params)
        
        logger.info(f'========== 易支付请求 ==========')
        logger.info(f'接口URL: {self.mapi_url}')
        logger.info(f'商户ID: {self.pid}')
        logger.info(f'订单号: {order_id}')
        logger.info(f'金额: {amount}')
        logger.info(f'支付方式: {pay_type}')
        logger.info(f'签名: {params["sign"]}')
        logger.info(f'完整参数: {params}')
        
        try:
            response = requests.post(self.mapi_url, data=params, timeout=10)
            logger.info(f'响应状态码: {response.status_code}')
            logger.info(f'响应内容: {response.text}')
            
            result = response.json()
            logger.info(f'解析结果: {result}')
            
            return result
        except Exception as e:
            logger.error(f'支付请求异常: {str(e)}')
            return {'code': 0, 'msg': f'请求失败: {str(e)}'}
    
    def query_order(self, order_id):
        """
        查询订单状态
        GET /api.php?act=order&pid={pid}&key={key}&out_trade_no={order_id}
        """
        # 演示模式
        if self.demo_mode:
            logger.info(f'演示模式：查询订单 {order_id}')
            # 演示模式下返回未支付状态，需要手动更新
            return {
                'code': 1,
                'msg': '演示模式：查询成功',
                'status': 0,  # 0=未支付（演示模式保持未支付状态）
                'out_trade_no': str(order_id),
                'money': '0.01'
            }
        
        url = f'{self.api_url}?act=order&pid={self.pid}&key={self.key}&out_trade_no={order_id}'
        
        logger.info(f'查询订单: {url}')
        
        try:
            response = requests.get(url, timeout=10)
            result = response.json()
            logger.info(f'查询结果: {result}')
            return result
        except Exception as e:
            logger.error(f'查询订单异常: {str(e)}')
            return {'code': 0, 'msg': str(e)}
    
    def refund_order(self, trade_no=None, out_trade_no=None, money=None):
        """
        订单退款
        POST /api.php?act=refund
        """
        url = f'{self.api_url}?act=refund'
        
        params = {
            'pid': self.pid,
            'key': self.key,
        }
        
        if trade_no:
            params['trade_no'] = trade_no
        if out_trade_no:
            params['out_trade_no'] = out_trade_no
        if money:
            params['money'] = f'{float(money):.2f}'
        
        logger.info(f'退款请求: {params}')
        
        try:
            response = requests.post(url, data=params, timeout=10)
            result = response.json()
            logger.info(f'退款结果: {result}')
            return result
        except Exception as e:
            logger.error(f'退款异常: {str(e)}')
            return {'code': 0, 'msg': str(e)}

