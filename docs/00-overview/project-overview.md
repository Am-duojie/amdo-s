# 项目总览

## 项目定位
本项目为“二手交易 + 回收 + 官方验（检验后上架）”的综合平台，包含用户端与管理端两套业务域。

## 技术栈（以代码为准）
- 后端：Django + DRF + SimpleJWT；Channels（WebSocket）
- 数据库：MySQL
- 前端：Vue 3 + Vite + Element Plus + Pinia

## 仓库结构快照
```
📄 .gitignore
📄 ADMIN_AUTH_FIX.md
📄 ADMIN_PERMISSION_TEST_GUIDE.md
📄 GIT_GITHUB_═Ω╚½╓╕─╧.md
📄 GIT_MANAGEMENT_GUIDE.md
📄 GIT_PULL_╧Ω╧╕╜Γ╩═.md
📄 IDE┤┐═╝╨╬╜τ├µGit═Ω╒√┴≈│╠.md
📄 IDE║╧▓ó╖╓╓º╡─╢α╓╓╖╜╖¿.md
📄 IDE╓╨║╧▓ó╖╓╓º╧Ω╧╕▓╜╓Φ.md
📄 IDE╓╨╩╣╙├Git═╝╨╬╜τ├µ╓╕─╧.md
📄 README.md
📄 RECYCLE_BUSINESS_PROCESS.md
📄 RECYCLE_DATA_FIX.md
📄 RECYCLE_PAYMENT_FIX.md
📄 app_public_key.pem
📁 backend
📄 backend/ALIPAY_NOTIFY_URL_CONFIG.md
📄 backend/ALIPAY_PAYMENT_DEVELOPMENT_GUIDE.md
📄 backend/ALIPAY_PRODUCT_RECOMMENDATION.md
📄 backend/ALIPAY_ROYALTY_SANDBOX_DEBUG_GUIDE.md
📄 backend/ALIPAY_SETTLEMENT_FAILURE_GUIDE.md
📄 backend/ALIPAY_SETUP.md
📄 backend/ALIPAY_SIGNATURE_FIX_SUMMARY.md
📄 backend/ALIPAY_TRANSFER_GUIDE.md
📄 backend/BUSINESS_FLOW_COMPLETE.md
📄 backend/COMPLETE_FEATURES_SUMMARY.md
📄 backend/INTRANET_PENETRATION_GUIDE.md
📄 backend/NGROK_USAGE.md
📄 backend/PAYMENT_CALLBACK_IMPLEMENTATION.md
📄 backend/PAYMENT_DEBUG_GUIDE.md
📄 backend/PAYMENT_FLOW_COMPLETE.md
📄 backend/PAYMENT_REDIRECT_FIX.md
📄 backend/PAYMENT_RETURN_FIX.md
📄 backend/RECYCLE_BUSINESS_FLOW.md
📄 backend/RECYCLE_VERIFIED_HANDBOOK.md
📄 backend/ROYALTY_FIX_SUMMARY.md
📄 backend/WINDOWS_PATH_SETUP.md
📄 backend/add_all_permissions.py
📄 backend/add_ngrok_to_path.ps1
📄 backend/all_products.csv
📄 backend/all_products_detailed.txt
📄 backend/all_products_full_analysis.txt
📁 backend/app
📁 backend/app/admin_api
📄 backend/app/consumers.py
📄 backend/app/routing.py
📁 backend/app/secondhand_app
📄 backend/app_public_key.pem
📄 backend/app_public_key_to_upload.txt
📄 backend/assign_categories.py
📄 backend/category_analysis.csv
📄 backend/check_alipay_config.py
📄 backend/check_and_fix_all_categories.py
📄 backend/check_desktop_computers.py
📄 backend/check_permissions.py
📄 backend/cleanup_verified.py
📄 backend/comprehensive_category_fix.py
📁 backend/core
📄 backend/core/__init__.py
📄 backend/core/asgi.py
📄 backend/core/settings.py
📄 backend/core/urls.py
📄 backend/core/wsgi.py
📁 backend/data
📄 backend/data/aihuishou_test.json
📁 backend/docs
📄 backend/docs/╓º╕╢▒ª╔│╧Σ╜╙┐┌╩ß└φ.md
📄 backend/export_all_products.py
📄 backend/export_all_products_for_analysis.py
📄 backend/export_all_products_for_full_analysis.py
📄 backend/export_products.py
📄 backend/fix_categories.py
📄 backend/fix_categories_manually.py
📄 backend/formatted_public_key.pem
📄 backend/manage.py
📄 backend/ngrok-backend.yml
📄 backend/ngrok-frontend.yml
📄 backend/ngrok.yml
📄 backend/permissions_config.json
📄 backend/product_samples.txt
📄 backend/requirements.txt
📁 backend/scripts
📄 backend/scripts/retry_settlement.py
📄 backend/scripts/settlement_self_check.py
📄 backend/setup_ngrok.ps1
📄 backend/setup_ngrok_config.ps1
📄 backend/start_ngrok.ps1
📄 backend/start_ngrok_backend.ps1
📄 backend/start_ngrok_both.ps1
📄 backend/start_ngrok_frontend.ps1
📄 backend/stop_ngrok.ps1
📄 backend/test_alipay_signature.py
📄 backend/test_alipay_transfer.py
📄 backend/test_payment.py
📄 backend/test_price_model.py
📄 backend/test_public_api.py
📄 backend/test_scraper.py
📄 backend/verify_categories.py
📄 backend/verify_drones.py
📄 backend/verify_fix.py
📄 backend/verify_permissions.py
📄 backend/watch_log.ps1
📄 backend/┼Σ╓├╢α╒╦║┼ngrok.ps1
📄 backend/┼└╚í╖■╬±╩╣╙├╦╡├≈.md
📄 backend/╓º╕╢╗╪╡≈╡╪╓╖┼Σ╓├╦╡├≈.md
📄 backend/╓╪╞⌠ngrok.ps1
📄 backend/╞⌠╢»ngrok╦∙╙╨╦φ╡└.ps1
📄 backend/╞⌠╢»╢α╒╦║┼ngrok.ps1
📄 backend/╣└╝█╦π╖¿╦╡├≈.md
📁 docs_and_scripts
📁 docs_and_scripts/backend
📄 docs_and_scripts/backend/ADMIN_AUTH_FIX.md
📄 docs_and_scripts/backend/ADMIN_PERMISSION_TEST_GUIDE.md
📄 docs_and_scripts/backend/ALIPAY_NOTIFY_URL_CONFIG.md
📄 docs_and_scripts/backend/ALIPAY_PAYMENT_DEVELOPMENT_GUIDE.md
📄 docs_and_scripts/backend/ALIPAY_PRODUCT_RECOMMENDATION.md
📄 docs_and_scripts/backend/ALIPAY_ROYALTY_SANDBOX_DEBUG_GUIDE.md
📄 docs_and_scripts/backend/ALIPAY_SETTLEMENT_FAILURE_GUIDE.md
📄 docs_and_scripts/backend/ALIPAY_SETUP.md
📄 docs_and_scripts/backend/ALIPAY_SIGNATURE_FIX_SUMMARY.md
📄 docs_and_scripts/backend/ALIPAY_TRANSFER_GUIDE.md
📄 docs_and_scripts/backend/Activate.ps1
📄 docs_and_scripts/backend/BUSINESS_FLOW_COMPLETE.md
📄 docs_and_scripts/backend/COMPLETE_FEATURES_SUMMARY.md
📄 docs_and_scripts/backend/GIT_GITHUB_═Ω╚½╓╕─╧.md
📄 docs_and_scripts/backend/GIT_MANAGEMENT_GUIDE.md
📄 docs_and_scripts/backend/GIT_PULL_╧Ω╧╕╜Γ╩═.md
📄 docs_and_scripts/backend/IDE┤┐═╝╨╬╜τ├µGit═Ω╒√┴≈│╠.md
📄 docs_and_scripts/backend/IDE║╧▓ó╖╓╓º╡─╢α╓╓╖╜╖¿.md
📄 docs_and_scripts/backend/IDE╓╨║╧▓ó╖╓╓º╧Ω╧╕▓╜╓Φ.md
📄 docs_and_scripts/backend/IDE╓╨╩╣╙├Git═╝╨╬╜τ├µ╓╕─╧.md
📄 docs_and_scripts/backend/INTRANET_PENETRATION_GUIDE.md
📄 docs_and_scripts/backend/LICENSE-SELECT2.md
📄 docs_and_scripts/backend/LICENSE.md
📄 docs_and_scripts/backend/NGROK_USAGE.md
📄 docs_and_scripts/backend/PAYMENT_CALLBACK_IMPLEMENTATION.md
📄 docs_and_scripts/backend/PAYMENT_DEBUG_GUIDE.md
📄 docs_and_scripts/backend/PAYMENT_FLOW_COMPLETE.md
📄 docs_and_scripts/backend/PAYMENT_REDIRECT_FIX.md
📄 docs_and_scripts/backend/PAYMENT_RETURN_FIX.md
📄 docs_and_scripts/backend/README.md
📄 docs_and_scripts/backend/RECYCLE_BUSINESS_FLOW.md
📄 docs_and_scripts/backend/RECYCLE_BUSINESS_PROCESS.md
📄 docs_and_scripts/backend/RECYCLE_DATA_FIX.md
📄 docs_and_scripts/backend/RECYCLE_PAYMENT_FIX.md
📄 docs_and_scripts/backend/ROYALTY_FIX_SUMMARY.md
📄 docs_and_scripts/backend/WINDOWS_PATH_SETUP.md
📄 docs_and_scripts/backend/add_all_permissions.py
📄 docs_and_scripts/backend/add_ngrok_to_path.ps1
📄 docs_and_scripts/backend/assign_categories.py
📄 docs_and_scripts/backend/check_alipay_config.py
📄 docs_and_scripts/backend/check_and_fix_all_categories.py
📄 docs_and_scripts/backend/check_desktop_computers.py
📄 docs_and_scripts/backend/check_permissions.py
📄 docs_and_scripts/backend/comprehensive_category_fix.py
📄 docs_and_scripts/backend/export_all_products.py
📄 docs_and_scripts/backend/export_all_products_for_analysis.py
📄 docs_and_scripts/backend/export_all_products_for_full_analysis.py
📄 docs_and_scripts/backend/export_products.py
📄 docs_and_scripts/backend/fix_categories.py
📄 docs_and_scripts/backend/fix_categories_manually.py
📄 docs_and_scripts/backend/manage.py
📄 docs_and_scripts/backend/retry_settlement.py
📄 docs_and_scripts/backend/settlement_self_check.py
📄 docs_and_scripts/backend/setup_ngrok.ps1
📄 docs_and_scripts/backend/setup_ngrok_config.ps1
📄 docs_and_scripts/backend/start_ngrok.ps1
📄 docs_and_scripts/backend/start_ngrok_backend.ps1
📄 docs_and_scripts/backend/start_ngrok_both.ps1
📄 docs_and_scripts/backend/start_ngrok_frontend.ps1
📄 docs_and_scripts/backend/stop_ngrok.ps1
📄 docs_and_scripts/backend/test_alipay_signature.py
📄 docs_and_scripts/backend/test_alipay_transfer.py
📄 docs_and_scripts/backend/test_payment.py
📄 docs_and_scripts/backend/test_price_model.py
📄 docs_and_scripts/backend/test_public_api.py
📄 docs_and_scripts/backend/test_scraper.py
📄 docs_and_scripts/backend/verify_categories.py
📄 docs_and_scripts/backend/verify_drones.py
📄 docs_and_scripts/backend/verify_fix.py
📄 docs_and_scripts/backend/verify_permissions.py
📄 docs_and_scripts/backend/watch_log.ps1
📄 docs_and_scripts/backend/┼Σ╓├╢α╒╦║┼ngrok.ps1
📄 docs_and_scripts/backend/┼└╚í╖■╬±╩╣╙├╦╡├≈.md
📄 docs_and_scripts/backend/╓º╕╢╗╪╡≈╡╪╓╖┼Σ╓├╦╡├≈.md
📄 docs_and_scripts/backend/╓º╕╢▒ª╔│╧Σ╜╙┐┌╩ß└φ.md
📄 docs_and_scripts/backend/╓╪╞⌠ngrok.ps1
📄 docs_and_scripts/backend/╖╓╓º╠ß╜╗╦╡├≈.md
📄 docs_and_scripts/backend/╞⌠╢»ngrok╦∙╙╨╦φ╡└.ps1
📄 docs_and_scripts/backend/╞⌠╢»╢α╒╦║┼ngrok.ps1
📄 docs_and_scripts/backend/╡Ñ╚╦┐¬╖ó╝≥╗»┴≈│╠.md
📄 docs_and_scripts/backend/╣└╝█╦π╖¿╦╡├≈.md
📄 docs_and_scripts/backend/╩╡╤Θ╨╘╣ª─▄┐¬╖ó╓╕─╧.md
📁 docs_and_scripts/frontend
📄 docs_and_scripts/frontend/CHANGELOG.md
📄 docs_and_scripts/frontend/HISTORY.md
📄 docs_and_scripts/frontend/LICENSE.md
📄 docs_and_scripts/frontend/MIGRATION_GUIDE.md
📄 docs_and_scripts/frontend/README.md
📄 docs_and_scripts/frontend/SECURITY.md
📄 docs_and_scripts/frontend/chat_design.md
📄 docs_and_scripts/frontend/release.md
📄 docs_and_scripts/frontend/vite.config.js
📄 docs_and_scripts/╥╫╠╘║≤╠¿╣▄└φ╧╡═│┐¬╖ó╦╡├≈.md
📁 frontend
📄 frontend/.env.example
📄 frontend/index.html
📄 frontend/package.json
📁 frontend/src
📄 frontend/src/App.vue
📁 frontend/src/admin
📁 frontend/src/api
📁 frontend/src/components
📁 frontend/src/composables
📁 frontend/src/data
📄 frontend/src/index.css
📄 frontend/src/main.js
📁 frontend/src/pages
📁 frontend/src/router
📁 frontend/src/stores
📁 frontend/src/styles
📁 frontend/src/utils
📄 frontend/vite.config.js
📄 tatus --short
📄 ╖╓╓º╠ß╜╗╦╡├≈.md
📄 ╡Ñ╚╦┐¬╖ó╝≥╗»┴≈│╠.md
📄 ╩╡╤Θ╨╘╣ª─▄┐¬╖ó╓╕─╧.md
```

## 文档适用范围
- 最后更新：2025-12-13
- 权威事实来源（SSOT）：路由/视图、models+migrations、.env.example/启动脚本（详见 `docs/README.md`）

