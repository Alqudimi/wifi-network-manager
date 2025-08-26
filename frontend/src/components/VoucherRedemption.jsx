import React from 'react';
import { Wifi, CheckCircle, XCircle, Loader2, CreditCard, Clock, Database } from 'lucide-react';
import { Button } from './ui/button';
import { Input } from './ui/input';
import { Label } from './ui/label';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './ui/card';
import { Alert, AlertDescription } from './ui/alert';
import { Badge } from './ui/badge';
import { formatDuration, formatDataSize, formatDateTime } from '../lib/utils';
import apiClient from '../lib/api';

const VoucherRedemption = () => {
  const [code, setCode] = React.useState('');
  const [loading, setLoading] = React.useState(false);
  const [checking, setChecking] = React.useState(false);
  const [result, setResult] = React.useState(null);
  const [error, setError] = React.useState('');
  const [voucherInfo, setVoucherInfo] = React.useState(null);

  const handleCheckVoucher = async () => {
    if (!code.trim()) {
      setError('يرجى إدخال كود الكرت');
      return;
    }

    setChecking(true);
    setError('');
    setVoucherInfo(null);

    try {
      const response = await apiClient.checkVoucher(code.trim().toUpperCase());
      setVoucherInfo(response);
    } catch (error) {
      setError(error.message || 'فشل في التحقق من الكرت');
    } finally {
      setChecking(false);
    }
  };

  const handleRedeemVoucher = async () => {
    if (!code.trim()) {
      setError('يرجى إدخال كود الكرت');
      return;
    }

    setLoading(true);
    setError('');
    setResult(null);

    try {
      const response = await apiClient.redeemVoucher(code.trim().toUpperCase());
      setResult({
        success: true,
        message: response.message,
        voucher: response.voucher,
        session: response.session
      });
      setCode('');
      setVoucherInfo(null);
    } catch (error) {
      setResult({
        success: false,
        message: error.message || 'فشل في استخدام الكرت'
      });
    } finally {
      setLoading(false);
    }
  };

  const handleCodeChange = (e) => {
    const value = e.target.value.toUpperCase();
    setCode(value);
    if (error) setError('');
    if (result) setResult(null);
    if (voucherInfo) setVoucherInfo(null);
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 dark:from-gray-900 dark:to-gray-800 flex items-center justify-center px-4 sm:px-6 lg:px-8">
      <div className="max-w-md w-full space-y-8">
        {/* Header */}
        <div className="text-center">
          <div className="flex justify-center">
            <div className="flex items-center justify-center w-16 h-16 bg-blue-600 rounded-full">
              <Wifi className="w-8 h-8 text-white" />
            </div>
          </div>
          <h2 className="mt-6 text-3xl font-bold text-gray-900 dark:text-white">
            الاتصال بشبكة Wi-Fi
          </h2>
          <p className="mt-2 text-sm text-gray-600 dark:text-gray-400">
            أدخل كود الكرت للحصول على إنترنت مجاني
          </p>
        </div>

        {/* Main Card */}
        <Card className="shadow-xl">
          <CardHeader>
            <CardTitle className="text-center flex items-center justify-center">
              <CreditCard className="w-5 h-5 ml-2" />
              استخدام كرت الإنترنت
            </CardTitle>
            <CardDescription className="text-center">
              أدخل الكود المكتوب على الكرت
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-6">
            {/* Code Input */}
            <div className="space-y-2">
              <Label htmlFor="code">كود الكرت</Label>
              <div className="flex space-x-2 space-x-reverse">
                <Input
                  id="code"
                  type="text"
                  value={code}
                  onChange={handleCodeChange}
                  placeholder="أدخل كود الكرت هنا"
                  className="text-center text-lg font-mono tracking-wider"
                  disabled={loading || checking}
                  maxLength={20}
                />
                <Button
                  type="button"
                  variant="outline"
                  onClick={handleCheckVoucher}
                  disabled={!code.trim() || checking || loading}
                >
                  {checking ? (
                    <Loader2 className="h-4 w-4 animate-spin" />
                  ) : (
                    'تحقق'
                  )}
                </Button>
              </div>
            </div>

            {/* Error Alert */}
            {error && (
              <Alert variant="destructive">
                <XCircle className="h-4 w-4" />
                <AlertDescription>{error}</AlertDescription>
              </Alert>
            )}

            {/* Voucher Info */}
            {voucherInfo && (
              <div className="space-y-4">
                <Alert variant={voucherInfo.is_valid ? "default" : "destructive"}>
                  <div className="flex items-center">
                    {voucherInfo.is_valid ? (
                      <CheckCircle className="h-4 w-4 text-green-500" />
                    ) : (
                      <XCircle className="h-4 w-4 text-red-500" />
                    )}
                    <AlertDescription className="mr-2">
                      {voucherInfo.validation_message}
                    </AlertDescription>
                  </div>
                </Alert>

                {voucherInfo.is_valid && (
                  <div className="bg-gray-50 dark:bg-gray-800 rounded-lg p-4 space-y-3">
                    <h4 className="font-medium text-gray-900 dark:text-white">
                      تفاصيل الكرت:
                    </h4>
                    
                    <div className="grid grid-cols-2 gap-4 text-sm">
                      <div>
                        <span className="text-gray-500 dark:text-gray-400">القيمة:</span>
                        <div className="font-medium">{voucherInfo.voucher.value}</div>
                      </div>
                      
                      {voucherInfo.voucher.duration_minutes && (
                        <div>
                          <span className="text-gray-500 dark:text-gray-400">المدة:</span>
                          <div className="font-medium">
                            {formatDuration(voucherInfo.voucher.duration_minutes)}
                          </div>
                        </div>
                      )}
                      
                      {voucherInfo.voucher.data_limit_mb && (
                        <div>
                          <span className="text-gray-500 dark:text-gray-400">حد البيانات:</span>
                          <div className="font-medium">
                            {formatDataSize(voucherInfo.voucher.data_limit_mb)}
                          </div>
                        </div>
                      )}
                      
                      <div>
                        <span className="text-gray-500 dark:text-gray-400">الاستخدام:</span>
                        <div className="font-medium">
                          {voucherInfo.voucher.usage_count} / {voucherInfo.voucher.max_usage_count}
                        </div>
                      </div>
                    </div>

                    {voucherInfo.voucher.expires_at && (
                      <div className="text-sm">
                        <span className="text-gray-500 dark:text-gray-400">ينتهي في:</span>
                        <div className="font-medium">
                          {formatDateTime(voucherInfo.voucher.expires_at)}
                        </div>
                      </div>
                    )}

                    {voucherInfo.active_sessions && voucherInfo.active_sessions.length > 0 && (
                      <div className="text-sm">
                        <Badge variant="secondary">
                          {voucherInfo.active_sessions.length} جلسة نشطة
                        </Badge>
                      </div>
                    )}
                  </div>
                )}
              </div>
            )}

            {/* Success/Error Result */}
            {result && (
              <Alert variant={result.success ? "default" : "destructive"}>
                <div className="flex items-center">
                  {result.success ? (
                    <CheckCircle className="h-4 w-4 text-green-500" />
                  ) : (
                    <XCircle className="h-4 w-4 text-red-500" />
                  )}
                  <AlertDescription className="mr-2">
                    {result.message}
                  </AlertDescription>
                </div>
              </Alert>
            )}

            {/* Success Details */}
            {result && result.success && result.session && (
              <div className="bg-green-50 dark:bg-green-900 rounded-lg p-4 space-y-3">
                <h4 className="font-medium text-green-900 dark:text-green-100 flex items-center">
                  <CheckCircle className="w-4 h-4 ml-2" />
                  تم الاتصال بنجاح!
                </h4>
                
                <div className="text-sm text-green-800 dark:text-green-200 space-y-2">
                  <div className="flex items-center justify-between">
                    <span>معرف الجلسة:</span>
                    <code className="bg-green-100 dark:bg-green-800 px-2 py-1 rounded text-xs">
                      {result.session.session_id.substring(0, 8)}...
                    </code>
                  </div>
                  
                  <div className="flex items-center justify-between">
                    <span>بدأت في:</span>
                    <span>{formatDateTime(result.session.started_at)}</span>
                  </div>
                  
                  {result.voucher.duration_minutes && (
                    <div className="flex items-center justify-between">
                      <span>المدة المتاحة:</span>
                      <span>{formatDuration(result.voucher.duration_minutes)}</span>
                    </div>
                  )}
                </div>
              </div>
            )}

            {/* Action Buttons */}
            <div className="space-y-3">
              {voucherInfo && voucherInfo.is_valid && (
                <Button
                  onClick={handleRedeemVoucher}
                  className="w-full"
                  disabled={loading}
                >
                  {loading ? (
                    <>
                      <Loader2 className="ml-2 h-4 w-4 animate-spin" />
                      جاري الاتصال...
                    </>
                  ) : (
                    <>
                      <Wifi className="ml-2 h-4 w-4" />
                      الاتصال بالإنترنت
                    </>
                  )}
                </Button>
              )}

              {!voucherInfo && code.trim() && (
                <Button
                  onClick={handleCheckVoucher}
                  variant="outline"
                  className="w-full"
                  disabled={checking}
                >
                  {checking ? (
                    <>
                      <Loader2 className="ml-2 h-4 w-4 animate-spin" />
                      جاري التحقق...
                    </>
                  ) : (
                    'التحقق من الكرت'
                  )}
                </Button>
              )}

              {result && result.success && (
                <Button
                  onClick={() => {
                    setCode('');
                    setResult(null);
                    setVoucherInfo(null);
                  }}
                  variant="outline"
                  className="w-full"
                >
                  استخدام كرت آخر
                </Button>
              )}
            </div>

            {/* Instructions */}
            <div className="bg-blue-50 dark:bg-blue-900 rounded-lg p-4">
              <h4 className="font-medium text-blue-900 dark:text-blue-100 mb-2">
                تعليمات الاستخدام:
              </h4>
              <ul className="text-sm text-blue-800 dark:text-blue-200 space-y-1">
                <li>• أدخل الكود المكتوب على الكرت</li>
                <li>• اضغط "تحقق" للتأكد من صحة الكرت</li>
                <li>• اضغط "الاتصال بالإنترنت" لبدء الجلسة</li>
                <li>• احتفظ بالكرت حتى انتهاء الجلسة</li>
              </ul>
            </div>
          </CardContent>
        </Card>

        {/* Footer */}
        <div className="text-center">
          <p className="text-xs text-gray-500 dark:text-gray-400">
            في حالة وجود مشكلة، يرجى التواصل مع الدعم الفني
          </p>
        </div>
      </div>
    </div>
  );
};

export default VoucherRedemption;

