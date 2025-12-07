from django.shortcuts import render
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from django.contrib.auth.models import User
from django.db.models import Q, Count
import logging

logger = logging.getLogger(__name__)
from .models import (
    Category, Product, ProductImage, Order, Message, Favorite, Address, UserProfile, RecycleOrder,
    VerifiedProduct, VerifiedProductImage, VerifiedOrder, VerifiedFavorite, Wallet, WalletTransaction
)
from .serializers import (
    UserSerializer, UserRegisterSerializer, UserUpdateSerializer,
    CategorySerializer, ProductSerializer, OrderSerializer,
    MessageSerializer, FavoriteSerializer, AddressSerializer, RecycleOrderSerializer,
    VerifiedProductSerializer, VerifiedProductImageSerializer, VerifiedOrderSerializer, VerifiedFavoriteSerializer
)


class UserViewSet(viewsets.ModelViewSet):
    """用户视图集"""
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    @action(detail=False, methods=['get', 'patch'], permission_classes=[IsAuthenticated])
    def me(self, request):
        """获取或更新当前用户信息"""
        if request.method == 'GET':
            serializer = UserSerializer(request.user, context={'request': request})
            return Response(serializer.data)
        elif request.method == 'PATCH':
            serializer = UserUpdateSerializer(request.user, data=request.data, partial=True, context={'request': request})
            if serializer.is_valid():
                serializer.save()
                # 使用 UserSerializer 返回完整数据，包括 alipay_login_id 等字段
                user_serializer = UserSerializer(request.user, context={'request': request})
                return Response(user_serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['post'], permission_classes=[])
    def register(self, request):
        """用户注册"""
        serializer = UserRegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            # 注册成功后自动创建Token
            from rest_framework.authtoken.models import Token
            token, _ = Token.objects.get_or_create(user=user)
            return Response({
                'message': '用户注册成功',
                'user': UserSerializer(user).data,
                'token': token.key
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['post'], permission_classes=[IsAuthenticated])
    def upload_avatar(self, request):
        """上传头像"""
        user = request.user
        profile, created = UserProfile.objects.get_or_create(user=user)
        
        if 'avatar' not in request.FILES:
            return Response({'detail': '未提供头像文件'}, status=status.HTTP_400_BAD_REQUEST)
        
        profile.avatar = request.FILES['avatar']
        profile.save()
        
        serializer = UserSerializer(user, context={'request': request})
        return Response(serializer.data)
    
    @action(detail=False, methods=['post'], permission_classes=[])
    def login(self, request):
        """用户登录"""
        from django.contrib.auth import authenticate
        from rest_framework.authtoken.models import Token
        
        username = request.data.get('username')
        password = request.data.get('password')
        
        if not username or not password:
            return Response({
                'error': '用户名和密码不能为空'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # 验证用户
        user = authenticate(username=username, password=password)
        
        if user is None:
            return Response({
                'error': '用户名或密码错误'
            }, status=status.HTTP_401_UNAUTHORIZED)
        
        if not user.is_active:
            return Response({
                'error': '账号已被禁用'
            }, status=status.HTTP_403_FORBIDDEN)
        
        # 获取或创建Token
        token, _ = Token.objects.get_or_create(user=user)
        
        return Response({
            'message': '登录成功',
            'token': token.key,
            'user': UserSerializer(user, context={'request': request}).data
        })
    
    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def wallet(self, request):
        """获取当前用户钱包信息"""
        wallet, created = Wallet.objects.get_or_create(user=request.user)
        page = int(request.query_params.get('page', 1))
        page_size = int(request.query_params.get('page_size', 20))
        
        # 获取交易记录（分页）
        transactions_qs = wallet.transactions.all()
        total = transactions_qs.count()
        transactions = transactions_qs[(page-1)*page_size: page*page_size]
        
        return Response({
            'balance': float(wallet.balance),
            'frozen_balance': float(wallet.frozen_balance),
            'transactions': [{
                'id': t.id,
                'transaction_type': t.transaction_type,
                'transaction_type_display': t.get_transaction_type_display(),
                'amount': float(t.amount),
                'balance_after': float(t.balance_after),
                'note': t.note,
                'created_at': t.created_at.isoformat(),
                'withdraw_status': t.withdraw_status,
                'withdraw_status_display': t.get_withdraw_status_display() if t.withdraw_status else None,
                'alipay_order_id': t.alipay_order_id if hasattr(t, 'alipay_order_id') else None,
            } for t in transactions],
            'total': total,
            'page': page,
            'page_size': page_size
        })
    
    @action(detail=False, methods=['post'], permission_classes=[IsAuthenticated])
    def withdraw(self, request):
        """提现到支付宝"""
        from decimal import Decimal
        from app.secondhand_app.alipay_client import AlipayClient
        import time
        
        amount = request.data.get('amount')
        alipay_account = request.data.get('alipay_account', '').strip()
        alipay_name = request.data.get('alipay_name', '').strip()
        
        if not amount:
            return Response({'detail': '提现金额不能为空'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            amount = Decimal(str(amount))
            if amount <= 0:
                return Response({'detail': '提现金额必须大于0'}, status=status.HTTP_400_BAD_REQUEST)
        except (ValueError, TypeError):
            return Response({'detail': '提现金额格式错误'}, status=status.HTTP_400_BAD_REQUEST)
        
        if not alipay_account:
            return Response({'detail': '支付宝账号不能为空'}, status=status.HTTP_400_BAD_REQUEST)
        
        # 获取用户钱包
        wallet, created = Wallet.objects.get_or_create(user=request.user)
        
        # 检查余额是否足够
        if wallet.balance < amount:
            return Response({'detail': '余额不足'}, status=status.HTTP_400_BAD_REQUEST)
        
        # 检查支付宝配置
        alipay = AlipayClient()
        is_valid, error_msg = alipay.validate_config()
        if not is_valid:
            return Response({'detail': f'支付宝配置未完成: {error_msg}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        # 创建提现交易记录（先冻结金额）
        transaction = WalletTransaction.objects.create(
            wallet=wallet,
            transaction_type='withdraw',
            amount=-amount,  # 负数表示支出
            balance_after=wallet.balance - amount,
            alipay_account=alipay_account,
            alipay_name=alipay_name,
            withdraw_status='pending',
            note=f'提现到支付宝: {alipay_account}'
        )
        
        # 扣除余额
        wallet.balance -= amount
        wallet.save()
        
        # 调用支付宝转账接口
        try:
            transfer_result = alipay.transfer_to_account(
                out_biz_no=f'withdraw_{request.user.id}_{int(time.time())}',
                payee_account=alipay_account,
                amount=float(amount),
                payee_real_name=alipay_name if alipay_name else None,
                remark=f'易淘账户提现'
            )
            
            if transfer_result.get('success'):
                # 提现成功
                transaction.withdraw_status = 'success'
                transaction.alipay_order_id = transfer_result.get('order_id', '')
                transaction.note = f'提现成功，支付宝订单号: {transfer_result.get("order_id", "")}'
                transaction.save()
                
                logger.info(f'提现成功: 用户ID={request.user.id}, 金额={amount}, 支付宝订单号={transfer_result.get("order_id", "")}')
                
                return Response({
                    'success': True,
                    'message': '提现成功',
                    'order_id': transfer_result.get('order_id', ''),
                    'balance': float(wallet.balance)
                })
            else:
                # 提现失败，退回余额
                wallet.balance += amount
                wallet.save()
                
                error_code = transfer_result.get('code', '')
                error_msg = transfer_result.get('msg', '提现失败')
                sub_code = transfer_result.get('sub_code', '')
                sub_msg = transfer_result.get('sub_msg', '')
                
                transaction.withdraw_status = 'failed'
                transaction.note = f'提现失败: {sub_msg or error_msg}'
                transaction.save()
                
                logger.error(f'提现失败: 用户ID={request.user.id}, code={error_code}, msg={error_msg}')
                
                return Response({
                    'success': False,
                    'detail': f'提现失败: {sub_msg or error_msg}',
                    'error_code': error_code,
                    'sub_code': sub_code
                }, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            # 异常时退回余额
            wallet.balance += amount
            wallet.save()
            
            transaction.withdraw_status = 'failed'
            transaction.note = f'提现异常: {str(e)}'
            transaction.save()
            
            logger.error(f'提现异常: 用户ID={request.user.id}, 错误={str(e)}', exc_info=True)
            
            return Response({
                'success': False,
                'detail': f'提现异常: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



class CategoryViewSet(viewsets.ReadOnlyModelViewSet):
    """分类视图集"""
    serializer_class = CategorySerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    
    def get_queryset(self):
        """按商品数量（热度）排序分类"""
        return Category.objects.annotate(
            product_count=Count('products', filter=Q(products__status='active'))
        ).order_by('-product_count', 'name')


class ProductViewSet(viewsets.ModelViewSet):
    """商品视图集"""
    queryset = Product.objects.filter(status='active')
    serializer_class = ProductSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    search_fields = ['title', 'description']
    ordering_fields = ['price', 'created_at', 'view_count']
    ordering = ['-created_at']

    def get_queryset(self):
        queryset = Product.objects.filter(status='active').select_related('category', 'seller')
        
        # 分类筛选（优先处理，确保分类筛选生效）
        category = self.request.query_params.get('category', None)
        if category:
            try:
                category_id = int(category)
                queryset = queryset.filter(category_id=category_id)
            except (ValueError, TypeError):
                # 如果category不是数字，尝试按名称查找
                queryset = queryset.filter(category__name=category)
        
        # 搜索功能
        search = self.request.query_params.get('search', None)
        if search:
            queryset = queryset.filter(
                Q(title__icontains=search) | Q(description__icontains=search)
            )
        
        # 成色筛选（支持多个成色，用逗号分隔）
        condition = self.request.query_params.get('condition', None)
        if condition:
            # 支持多个成色条件（如：new,like_new,good）
            if ',' in condition:
                conditions = [c.strip() for c in condition.split(',') if c.strip()]
                queryset = queryset.filter(condition__in=conditions)
            else:
                queryset = queryset.filter(condition=condition)
        
        # 价格范围筛选
        min_price = self.request.query_params.get('min_price', None)
        max_price = self.request.query_params.get('max_price', None)
        if min_price:
            try:
                queryset = queryset.filter(price__gte=float(min_price))
            except (ValueError, TypeError):
                pass
        if max_price:
            try:
                queryset = queryset.filter(price__lte=float(max_price))
            except (ValueError, TypeError):
                pass
        
        return queryset

    def perform_create(self, serializer):
        """创建商品时设置卖家为当前用户"""
        serializer.save(seller=self.request.user)

    @action(detail=True, methods=['patch'], permission_classes=[IsAuthenticated])
    def update_status(self, request, pk=None):
        """更新商品状态"""
        product = self.get_object()
        if product.seller != request.user:
            return Response({'detail': '无权限操作'}, status=status.HTTP_403_FORBIDDEN)
        
        status_value = request.data.get('status')
        if status_value not in dict(Product.STATUS_CHOICES).keys():
            return Response({'detail': '无效的状态值'}, status=status.HTTP_400_BAD_REQUEST)
        
        product.status = status_value
        product.save()
        serializer = ProductSerializer(product, context={'request': request})
        return Response(serializer.data)

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def upload_images(self, request, pk=None):
        """上传商品图片"""
        product = self.get_object()
        if product.seller != request.user:
            return Response({'detail': '无权限操作'}, status=status.HTTP_403_FORBIDDEN)
        
        images = request.FILES.getlist('images')
        if not images:
            return Response({'detail': '未提供图片文件'}, status=status.HTTP_400_BAD_REQUEST)
        
        # 如果没有主图，则设置第一张图片为主图
        has_primary = ProductImage.objects.filter(product=product, is_primary=True).exists()
        
        for i, image in enumerate(images):
            is_primary = not has_primary and i == 0
            ProductImage.objects.create(
                product=product,
                image=image,
                is_primary=is_primary
            )
            
            if is_primary:
                has_primary = True
                
        serializer = ProductSerializer(product, context={'request': request})
        return Response(serializer.data)

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def favorite(self, request, pk=None):
        """收藏商品"""
        product = self.get_object()
        favorite, created = Favorite.objects.get_or_create(
            user=request.user,
            product=product
        )
        if created:
            return Response({'detail': '收藏成功'})
        else:
            return Response({'detail': '已收藏'})

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def unfavorite(self, request, pk=None):
        """取消收藏商品"""
        product = self.get_object()
        try:
            favorite = Favorite.objects.get(user=request.user, product=product)
            favorite.delete()
            return Response({'detail': '已取消收藏'})
        except Favorite.DoesNotExist:
            return Response({'detail': '未收藏该商品'})

    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def my_products(self, request):
        """获取当前用户发布的商品（包括所有状态）"""
        products = Product.objects.filter(seller=request.user).order_by('-created_at')
        serializer = ProductSerializer(products, many=True, context={'request': request})
        return Response(serializer.data)

    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def my_sales(self, request):
        """获取当前用户作为卖家的订单（含结算状态与账户）"""
        orders = Order.objects.filter(product__seller=request.user).order_by('-created_at')
        serializer = OrderSerializer(orders, many=True, context={'request': request})
        return Response(serializer.data)


class OrderViewSet(viewsets.ModelViewSet):
    """订单视图集"""
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """只显示当前用户的订单，并优化查询"""
        # 如果请求参数中有verified=true，只返回官方验货订单（且只返回买家订单）
        verified = self.request.query_params.get('verified', '').lower()
        if verified == 'true':
            # 官方验货模式下，只返回买家订单，且商品成色必须是new, like_new, good
            queryset = Order.objects.filter(
                buyer=self.request.user,
                product__condition__in=['new', 'like_new', 'good']
            ).select_related('buyer', 'product', 'product__seller', 'product__category').prefetch_related('product__images')
        else:
            # 普通模式：返回买家和卖家订单
            queryset = Order.objects.filter(
                Q(buyer=self.request.user) | Q(product__seller=self.request.user)
            ).select_related('buyer', 'product', 'product__seller', 'product__category').prefetch_related('product__images').distinct()
        
        return queryset

    def perform_create(self, serializer):
        """创建订单"""
        serializer.save(buyer=self.request.user)

    @action(detail=True, methods=['patch'], permission_classes=[IsAuthenticated])
    def update_status(self, request, pk=None):
        """更新订单状态"""
        order = self.get_object()
        # 检查是否有权限更新订单状态
        if order.buyer != request.user and order.product.seller != request.user:
            return Response({'detail': '无权限操作'}, status=status.HTTP_403_FORBIDDEN)
        
        status_value = request.data.get('status')
        if status_value not in dict(Order.STATUS_CHOICES).keys():
            return Response({'detail': '无效的状态值'}, status=status.HTTP_400_BAD_REQUEST)
        
        order.status = status_value
        order.save()

        # 买家确认收货后触发分账结算（普通订单）
        try:
            from django.conf import settings
            from django.utils import timezone
            if status_value == 'completed' and getattr(settings, 'SETTLE_ON_ORDER_COMPLETED', False) and getattr(settings, 'ENABLE_ALIPAY_ROYALTY', False):
                if not order.delivered_at:
                    order.delivered_at = timezone.now()
                    order.save()
                # 仅当订单已支付且分账待处理
                if getattr(order, 'settlement_status', 'pending') == 'pending' and order.status in ['completed']:
                    seller_profile = getattr(order.product.seller, 'profile', None)
                    seller_login_id = seller_profile.alipay_login_id if seller_profile else ''
                    seller_user_id = seller_profile.alipay_user_id if seller_profile else ''
                    if not seller_login_id:
                        logger.error(f'分账暂缓：卖家未绑定支付宝登录账号，order_id={order.id}')
                        # 保持为pending，以便卖家绑定后自动结算
                        order.settlement_status = 'pending'
                        order.save()
                    else:
                        from app.secondhand_app.alipay_client import AlipayClient
                        alipay = AlipayClient()
                        # 交易号优先用记录的，其次主动查询
                        trade_no = getattr(order, 'alipay_trade_no', '')
                        if not trade_no:
                            query = alipay.query_trade(f'normal_{order.id}')
                            if query.get('success'):
                                trade_no = query.get('trade_no', '')
                        if not trade_no:
                            logger.error(f'分账暂缓：无法获取支付宝交易号，order_id={order.id}')
                            # 保持为pending，待支付回调或同步查询后再结算
                            order.settlement_status = 'pending'
                            order.save()
                        else:
                            # 计算分账金额（卖家为商品价格，佣金为差额）
                            from decimal import Decimal
                            seller_amount = Decimal(str(order.product.price))
                            commission_amount = Decimal(str(order.total_price)) - seller_amount
                            if commission_amount < 0:
                                commission_amount = Decimal('0.00')
                            out_request_no = f'settle_{order.id}_{int(timezone.now().timestamp())}'
                            # 根据支付宝分账文档，需要提供转出方信息（商户账号）
                            # 获取商户的支付宝账号（从配置或订单中获取）
                            # 注意：在沙箱环境中，转出方通常是商户账号
                            if seller_user_id:
                                result = alipay.settle_order(
                                    trade_no=trade_no,
                                    out_request_no=out_request_no,
                                    splits=[{
                                        'trans_in': seller_user_id,
                                        'trans_in_type': 'userId',
                                        'amount': float(seller_amount),
                                        'desc': '易淘分账-卖家',
                                        'royalty_scene': '平台服务费'
                                    }],
                                    # 转出方信息（可选，如果不提供则使用商户账号）
                                    # trans_out 和 trans_out_type 可以从订单或配置中获取
                                )
                            else:
                                result = alipay.settle_order(
                                    trade_no=trade_no,
                                    out_request_no=out_request_no,
                                    splits=[{
                                        'trans_in': seller_login_id,
                                        'trans_in_type': 'loginName',
                                        'amount': float(seller_amount),
                                        'desc': '易淘分账-卖家',
                                        'royalty_scene': '平台服务费'
                                    }],
                                    # 转出方信息（可选，如果不提供则使用商户账号）
                                )
                            if result.get('success'):
                                order.settlement_status = 'settled'
                                order.settled_at = timezone.now()
                                order.settle_request_no = out_request_no
                                order.seller_settle_amount = seller_amount
                                order.platform_commission_amount = commission_amount
                                order.settlement_method = 'ROYALTY'
                                order.save()
                                try:
                                    wallet, _ = Wallet.objects.get_or_create(user=order.product.seller)
                                    WalletTransaction.objects.create(
                                        wallet=wallet,
                                        transaction_type='income',
                                        amount=seller_amount,
                                        balance_after=wallet.balance,
                                        related_market_order=order,
                                        alipay_account=(seller_user_id or seller_login_id),
                                        alipay_name=(seller_profile.alipay_real_name if seller_profile else ''),
                                        note=f'订单#{order.id} 分账完成，资金已存入支付宝: {(seller_user_id or seller_login_id)}'
                                    )
                                except Exception:
                                    pass
                            else:
                                order.settlement_status = 'failed'
                                order.settle_request_no = out_request_no
                                order.save()
                                logger.error(f"分账失败: code={result.get('code')}, msg={result.get('msg')}, sub={result.get('sub_code')} {result.get('sub_msg')}")
                                try:
                                    from app.admin_api.models import AdminAuditLog
                                    AdminAuditLog.objects.create(
                                        actor=None,
                                        target_type='Order',
                                        target_id=order.id,
                                        action='settlement_auto',
                                        snapshot_json={
                                            'result': 'failed',
                                            'code': result.get('code'),
                                            'msg': result.get('msg'),
                                            'sub_code': result.get('sub_code'),
                                            'sub_msg': result.get('sub_msg')
                                        }
                                    )
                                except Exception:
                                    pass
                                try:
                                    if getattr(settings, 'SETTLEMENT_FALLBACK_TO_TRANSFER', False):
                                        out_biz_no = f'settle_transfer_{order.id}_{int(timezone.now().timestamp())}'
                                        transfer_res = alipay.transfer_to_account(
                                            out_biz_no=out_biz_no,
                                            payee_account=(seller_login_id or seller_user_id),
                                            amount=float(seller_amount),
                                            payee_real_name=(seller_profile.alipay_real_name if seller_profile else None),
                                            remark='易淘分账-转账代结算'
                                        )
                                        if transfer_res.get('success'):
                                            order.settlement_status = 'settled'
                                            order.settled_at = timezone.now()
                                            order.platform_commission_amount = commission_amount
                                            order.seller_settle_amount = seller_amount
                                            order.settlement_method = 'TRANSFER'
                                            order.transfer_order_id = transfer_res.get('order_id','')
                                            order.save()
                                            logger.info(f"分账失败后转账代结算成功: order_id={order.id}")
                                            try:
                                                wallet, _ = Wallet.objects.get_or_create(user=order.product.seller)
                                                WalletTransaction.objects.create(
                                                    wallet=wallet,
                                                    transaction_type='income',
                                                    amount=seller_amount,
                                                    balance_after=wallet.balance,
                                                    related_market_order=order,
                                                    alipay_account=(seller_user_id or seller_login_id),
                                                    alipay_name=(seller_profile.alipay_real_name if seller_profile else ''),
                                                    alipay_order_id=transfer_res.get('order_id',''),
                                                    note=f'订单#{order.id} 转账代结算成功，资金已存入支付宝: {(seller_user_id or seller_login_id)}'
                                                )
                                            except Exception:
                                                pass
                                        else:
                                            logger.error(f"转账代结算失败: code={transfer_res.get('code')}, msg={transfer_res.get('msg')}, sub={transfer_res.get('sub_code')} {transfer_res.get('sub_msg')}")
                                except Exception as e:
                                    logger.error(f'转账代结算异常: {str(e)}', exc_info=True)
        except Exception as e:
            logger.error(f'订单分账异常: {str(e)}', exc_info=True)
        serializer = OrderSerializer(order)
        return Response(serializer.data)


class MessageViewSet(viewsets.ModelViewSet):
    """消息视图集"""
    queryset = Message.objects.all()
    serializer_class = MessageSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """只显示当前用户发送或接收的消息"""
        return Message.objects.filter(
            Q(sender=self.request.user) | Q(receiver=self.request.user)
        )

    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def conversations(self, request):
        """获取对话列表（与当前用户有过消息交流的用户）"""
        # 获取与当前用户有消息往来的用户
        sent_messages = Message.objects.filter(sender=request.user).select_related('receiver')
        received_messages = Message.objects.filter(receiver=request.user).select_related('sender')
        
        # 提取用户列表
        user_ids = set()
        for msg in sent_messages:
            user_ids.add(msg.receiver.id)
        for msg in received_messages:
            user_ids.add(msg.sender.id)
            
        # 排除自己
        user_ids.discard(request.user.id)
        
        # 获取用户信息
        users = User.objects.filter(id__in=user_ids)
        serializer = UserSerializer(users, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def with_user(self, request):
        """获取与指定用户的消息记录"""
        user_id = request.query_params.get('user_id')
        if not user_id:
            return Response({'detail': '缺少用户ID参数'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            other_user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response({'detail': '用户不存在'}, status=status.HTTP_404_NOT_FOUND)
        
        messages = Message.objects.filter(
            (Q(sender=request.user) & Q(receiver=other_user)) |
            (Q(sender=other_user) & Q(receiver=request.user))
        ).order_by('created_at')
        
        serializer = MessageSerializer(messages, many=True, context={'request': request})
        return Response(serializer.data)


class FavoriteViewSet(viewsets.ModelViewSet):
    """收藏视图集"""
    queryset = Favorite.objects.all()
    serializer_class = FavoriteSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """只显示当前用户的收藏"""
        return Favorite.objects.filter(user=self.request.user)

    def create(self, request, *args, **kwargs):
        """添加收藏"""
        product_id = request.data.get('product_id')
        if not product_id:
            return Response({'detail': '缺少商品ID'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            product = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            return Response({'detail': '商品不存在'}, status=status.HTTP_404_NOT_FOUND)
        
        favorite, created = Favorite.objects.get_or_create(
            user=request.user,
            product=product
        )
        
        if created:
            serializer = FavoriteSerializer(favorite, context={'request': request})
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response({'detail': '商品已在收藏夹中'}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['post'], permission_classes=[IsAuthenticated])
    def remove(self, request):
        """取消收藏"""
        product_id = request.data.get('product_id')
        if not product_id:
            return Response({'detail': '缺少商品ID'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            favorite = Favorite.objects.get(user=request.user, product_id=product_id)
            favorite.delete()
            return Response({'detail': '已取消收藏'})
        except Favorite.DoesNotExist:
            return Response({'detail': '未收藏该商品'}, status=status.HTTP_400_BAD_REQUEST)


class AddressViewSet(viewsets.ModelViewSet):
    """收货地址视图集"""
    queryset = Address.objects.all()
    serializer_class = AddressSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """只显示当前用户的收货地址"""
        return Address.objects.filter(user=self.request.user)


class RecycleOrderViewSet(viewsets.ModelViewSet):
    """回收订单视图集"""
    queryset = RecycleOrder.objects.all()
    serializer_class = RecycleOrderSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """只显示当前用户的回收订单"""
        return RecycleOrder.objects.filter(user=self.request.user)

    @action(detail=True, methods=['get'])
    def inspection_report(self, request, pk=None):
        """获取订单的质检报告"""
        order = self.get_object()
        # 检查订单是否属于当前用户
        if order.user != request.user:
            return Response({'detail': '无权访问'}, status=status.HTTP_403_FORBIDDEN)
        
        # 获取最新的质检报告
        from app.admin_api.models import AdminInspectionReport
        try:
            report = AdminInspectionReport.objects.filter(order=order).order_by('-created_at').first()
            if report:
                return Response({
                    'id': report.id,
                    'check_items': report.check_items,
                    'remarks': report.remarks,
                    'created_at': report.created_at
                })
            else:
                return Response({'detail': '暂无质检报告'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.error(f'获取质检报告失败: {e}')
            return Response({'detail': '获取质检报告失败'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=False, methods=['post'], permission_classes=[])
    def estimate(self, request):
        """估价接口 - 使用智能估价模型"""
        device_type = request.data.get('device_type')
        brand = request.data.get('brand')
        model = request.data.get('model')
        storage = request.data.get('storage', '')
        condition = request.data.get('condition', 'good')
        release_year = request.data.get('release_year')  # 可选：发布年份

        if not all([device_type, brand, model]):
            return Response({'error': '缺少必要参数'}, status=status.HTTP_400_BAD_REQUEST)

        # 使用价格服务进行估价（支持第三方API和智能模型）
        from .price_service import price_service
        estimated_price, from_api = price_service.estimate(device_type, brand, model, storage, condition)
        
        # 如果价格服务返回0，尝试使用智能估价模型
        if estimated_price == 0 and device_type == '手机':
            try:
                from .price_model import price_model
                estimated_price = price_model.estimate(brand, model, storage, condition, release_year)
                from_api = False  # 使用本地模型
            except Exception as e:
                logger.warning(f"智能估价模型失败: {e}")
        
        if estimated_price == 0:
            return Response({
                'error': '无法估算价格，请检查设备信息是否正确',
                'suggestions': [
                    '确认品牌和型号是否正确',
                    '确认存储容量格式（如：128GB、256GB）',
                    '如果设备较新，价格数据可能尚未更新'
                ]
            }, status=status.HTTP_400_BAD_REQUEST)
        
        bonus = self._calculate_bonus()  # 计算加价

        return Response({
            'estimated_price': float(estimated_price),
            'bonus': float(bonus),
            'total_price': float(estimated_price + bonus),
            'source': 'api' if from_api else 'model',  # 标识价格来源：api/model/local
            'currency': 'CNY',
            'unit': '元'
        })

    def _calculate_price(self, device_type, brand, model, storage, condition):
        """计算基础价格"""
        # 基础价格表（示例数据，实际应该从数据库或配置文件读取）
        base_prices = {
            '手机': {
                '苹果': {
                    'iPhone 15 Pro Max': {'128GB': 6500, '256GB': 7200, '512GB': 8500, '1TB': 10000},
                    'iPhone 15 Pro': {'128GB': 5500, '256GB': 6200, '512GB': 7500},
                    'iPhone 15': {'128GB': 4500, '256GB': 5200, '512GB': 6500},
                    'iPhone 14 Pro Max': {'128GB': 5500, '256GB': 6200, '512GB': 7500, '1TB': 9000},
                    'iPhone 14 Pro': {'128GB': 4800, '256GB': 5500, '512GB': 6800},
                    'iPhone 14': {'128GB': 3800, '256GB': 4500, '512GB': 5800},
                    'iPhone 13 Pro Max': {'128GB': 4500, '256GB': 5200, '512GB': 6500, '1TB': 8000},
                    'iPhone 13 Pro': {'128GB': 4000, '256GB': 4700, '512GB': 6000},
                    'iPhone 13': {'128GB': 3200, '256GB': 3900, '512GB': 5200},
                },
                '华为': {
                    'Mate 60 Pro': {'256GB': 4500, '512GB': 5500, '1TB': 6500},
                    'Mate 60': {'256GB': 3800, '512GB': 4800},
                    'P60 Pro': {'256GB': 3500, '512GB': 4500},
                    'P60': {'128GB': 2800, '256GB': 3500},
                },
                '小米': {
                    '小米14 Pro': {'256GB': 2800, '512GB': 3500, '1TB': 4200},
                    '小米14': {'256GB': 2200, '512GB': 2800},
                    '小米13 Ultra': {'256GB': 3000, '512GB': 3800},
                    '小米13': {'128GB': 1800, '256GB': 2400, '512GB': 3000},
                },
                'vivo': {
                    'X100 Pro': {'256GB': 3200, '512GB': 4000},
                    'X100': {'256GB': 2500, '512GB': 3200},
                },
                'OPPO': {
                    'Find X6 Pro': {'256GB': 3000, '512GB': 3800},
                    'Find X6': {'256GB': 2400, '512GB': 3000},
                },
            },
            '平板': {
                '苹果': {
                    'iPad Pro 12.9': {'128GB': 4500, '256GB': 5500, '512GB': 7000, '1TB': 9000},
                    'iPad Pro 11': {'128GB': 3500, '256GB': 4500, '512GB': 6000, '1TB': 8000},
                    'iPad Air': {'64GB': 2500, '256GB': 3500},
                    'iPad': {'64GB': 1800, '256GB': 2800},
                },
                '华为': {
                    'MatePad Pro': {'128GB': 2500, '256GB': 3200},
                    'MatePad': {'64GB': 1200, '128GB': 1800},
                },
            },
            '笔记本': {
                '苹果': {
                    'MacBook Pro 16': {'512GB': 8000, '1TB': 10000, '2TB': 12000},
                    'MacBook Pro 14': {'512GB': 7000, '1TB': 9000, '2TB': 11000},
                    'MacBook Air': {'256GB': 5500, '512GB': 7000, '1TB': 9000},
                },
                '联想': {
                    'ThinkPad X1': {'512GB': 4500, '1TB': 5500},
                    '小新16': {'512GB': 3000, '1TB': 4000},
                },
            },
        }

        # 获取基础价格
        try:
            base_price = base_prices.get(device_type, {}).get(brand, {}).get(model, {}).get(storage, 0)
            if base_price == 0:
                # 如果没有找到精确匹配，尝试模糊匹配
                for key, value in base_prices.get(device_type, {}).get(brand, {}).items():
                    if key in model or model in key:
                        base_price = value.get(storage, list(value.values())[0] if value else 0)
                        break
        except:
            base_price = 1000  # 默认价格

        # 根据成色调整价格
        condition_multipliers = {
            'new': 1.0,
            'like_new': 0.85,
            'good': 0.7,
            'fair': 0.5,
            'poor': 0.3
        }
        multiplier = condition_multipliers.get(condition, 0.7)

        return base_price * multiplier

    def _calculate_bonus(self):
        """计算加价（活动加价）"""
        # 示例：活动期间加价150元
        return 150


class VerifiedProductViewSet(viewsets.ModelViewSet):
    """官方验货商品视图集"""
    queryset = VerifiedProduct.objects.all()
    serializer_class = VerifiedProductSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        """获取商品列表，支持筛选"""
        queryset = VerifiedProduct.objects.filter(status='active').select_related(
            'seller', 'category'
        ).prefetch_related('images').order_by('-created_at')
        
        # 分类筛选
        category_id = self.request.query_params.get('category')
        if category_id:
            queryset = queryset.filter(category_id=category_id)
        
        # 搜索
        search = self.request.query_params.get('search')
        if search:
            queryset = queryset.filter(
                Q(title__icontains=search) | Q(description__icontains=search)
            )
        
        # 成色筛选
        condition = self.request.query_params.get('condition')
        if condition:
            queryset = queryset.filter(condition=condition)
        
        # 品牌筛选
        brand = self.request.query_params.get('brand')
        if brand:
            queryset = queryset.filter(brand__icontains=brand)
        
        # 价格范围筛选
        min_price = self.request.query_params.get('min_price')
        max_price = self.request.query_params.get('max_price')
        if min_price:
            queryset = queryset.filter(price__gte=min_price)
        if max_price:
            queryset = queryset.filter(price__lte=max_price)
        
        # 排序
        ordering = self.request.query_params.get('ordering', '-created_at')
        if ordering:
            queryset = queryset.order_by(ordering)
        
        return queryset

    def perform_create(self, serializer):
        """创建商品"""
        serializer.save(seller=self.request.user)

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def upload_images(self, request, pk=None):
        """上传商品图片"""
        product = self.get_object()
        if product.seller != request.user:
            return Response({'detail': '无权限操作'}, status=status.HTTP_403_FORBIDDEN)
        
        images = request.FILES.getlist('images')
        if not images:
            return Response({'detail': '未提供图片文件'}, status=status.HTTP_400_BAD_REQUEST)
        
        has_primary = VerifiedProductImage.objects.filter(product=product, is_primary=True).exists()
        
        for i, image in enumerate(images):
            is_primary = not has_primary and i == 0
            VerifiedProductImage.objects.create(
                product=product,
                image=image,
                is_primary=is_primary
            )
            
            if is_primary:
                has_primary = True
                
        serializer = VerifiedProductSerializer(product, context={'request': request})
        return Response(serializer.data)

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def favorite(self, request, pk=None):
        """收藏商品"""
        product = self.get_object()
        favorite, created = VerifiedFavorite.objects.get_or_create(
            user=request.user,
            product=product
        )
        if created:
            return Response({'detail': '收藏成功'})
        else:
            return Response({'detail': '已收藏'})

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def unfavorite(self, request, pk=None):
        """取消收藏商品"""
        product = self.get_object()
        try:
            favorite = VerifiedFavorite.objects.get(user=request.user, product=product)
            favorite.delete()
            return Response({'detail': '已取消收藏'})
        except VerifiedFavorite.DoesNotExist:
            return Response({'detail': '未收藏该商品'})

    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def my_products(self, request):
        """获取当前用户发布的官方验货商品"""
        products = VerifiedProduct.objects.filter(seller=request.user).order_by('-created_at')
        serializer = VerifiedProductSerializer(products, many=True, context={'request': request})
        return Response(serializer.data)


class VerifiedOrderViewSet(viewsets.ModelViewSet):
    """官方验货订单视图集"""
    queryset = VerifiedOrder.objects.all()
    serializer_class = VerifiedOrderSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """只显示当前用户的订单"""
        return VerifiedOrder.objects.filter(
            buyer=self.request.user
        ).select_related('buyer', 'product', 'product__seller', 'product__category').prefetch_related('product__images')

    def perform_create(self, serializer):
        """创建订单"""
        serializer.save(buyer=self.request.user)

    @action(detail=True, methods=['patch'], permission_classes=[IsAuthenticated])
    def update_status(self, request, pk=None):
        """更新订单状态"""
        order = self.get_object()
        if order.buyer != request.user:
            return Response({'detail': '无权限操作'}, status=status.HTTP_403_FORBIDDEN)
        
        status_value = request.data.get('status')
        if status_value not in dict(VerifiedOrder.STATUS_CHOICES).keys():
            return Response({'detail': '无效的状态值'}, status=status.HTTP_400_BAD_REQUEST)
        
        order.status = status_value
        order.save()
        # 官方验货订单完成后，同步触发分账（卖家为官方商品卖家）
        try:
            from django.conf import settings
            from django.utils import timezone
            if status_value == 'completed' and getattr(settings, 'SETTLE_ON_ORDER_COMPLETED', False) and getattr(settings, 'ENABLE_ALIPAY_ROYALTY', False):
                if not order.delivered_at:
                    order.delivered_at = timezone.now()
                    order.save()
                seller_profile = getattr(order.product.seller, 'profile', None)
                seller_login_id = seller_profile.alipay_login_id if seller_profile else ''
                if not seller_login_id:
                    logger.error(f'分账暂缓：卖家未绑定支付宝登录账号，verified_order_id={order.id}')
                    # 保持待分账，等待卖家绑定后自动结算
                    if hasattr(order, 'settlement_status'):
                        order.settlement_status = 'pending'
                        order.save()
                else:
                    from app.secondhand_app.alipay_client import AlipayClient
                    alipay = AlipayClient()
                    trade_no = getattr(order, 'alipay_trade_no', '')
                    if not trade_no:
                        query = alipay.query_trade(f'verified_{order.id}')
                        if query.get('success'):
                            trade_no = query.get('trade_no', '')
                    if not trade_no:
                        logger.error(f'分账暂缓：无法获取支付宝交易号，verified_order_id={order.id}')
                        if hasattr(order, 'settlement_status'):
                            order.settlement_status = 'pending'
                            order.save()
                    else:
                        from decimal import Decimal
                        seller_amount = Decimal(str(order.product.price))
                        commission_amount = Decimal(str(order.total_price)) - seller_amount
                        if commission_amount < 0:
                            commission_amount = Decimal('0.00')
                        out_request_no = f'settle_verified_{order.id}_{int(timezone.now().timestamp())}'
                        result = alipay.settle_order(
                            trade_no=trade_no,
                            out_request_no=out_request_no,
                            splits=[{
                                'trans_in': seller_login_id,
                                'trans_in_type': 'loginName',
                                'amount': float(seller_amount),
                                'desc': '易淘分账-卖家(官方验货)',
                                'royalty_scene': '平台服务费'
                            }]
                        )
                        if result.get('success'):
                            if hasattr(order, 'settlement_status'):
                                order.settlement_status = 'settled'
                                order.settled_at = timezone.now()
                                order.settle_request_no = out_request_no
                                order.seller_settle_amount = seller_amount
                                order.platform_commission_amount = commission_amount
                                order.save()
                        else:
                            if hasattr(order, 'settlement_status'):
                                order.settlement_status = 'failed'
                                order.settle_request_no = out_request_no
                                order.save()
                            logger.error(f"验货分账失败: code={result.get('code')}, msg={result.get('msg')}, sub={result.get('sub_code')} {result.get('sub_msg')}")
                            try:
                                from app.admin_api.models import AdminAuditLog
                                AdminAuditLog.objects.create(
                                    actor=None,
                                    target_type='VerifiedOrder',
                                    target_id=order.id,
                                    action='settlement_auto',
                                    snapshot_json={
                                        'result': 'failed',
                                        'code': result.get('code'),
                                        'msg': result.get('msg'),
                                        'sub_code': result.get('sub_code'),
                                        'sub_msg': result.get('sub_msg')
                                    }
                                )
                            except Exception:
                                pass
        except Exception as e:
            logger.error(f'验货订单分账异常: {str(e)}', exc_info=True)
        serializer = VerifiedOrderSerializer(order)
        return Response(serializer.data)


class VerifiedFavoriteViewSet(viewsets.ModelViewSet):
    """官方验货收藏视图集"""
    queryset = VerifiedFavorite.objects.all()
    serializer_class = VerifiedFavoriteSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """只显示当前用户的收藏"""
        return VerifiedFavorite.objects.filter(
            user=self.request.user
        ).select_related('user', 'product', 'product__seller').prefetch_related('product__images').order_by('-created_at')
