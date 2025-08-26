import React from 'react';
import { 
  Users, 
  CreditCard, 
  Wifi, 
  Activity,
  TrendingUp,
  TrendingDown,
  BarChart3,
  Clock
} from 'lucide-react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './ui/card';
import { Button } from './ui/button';
import { Badge } from './ui/badge';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, BarChart, Bar } from 'recharts';
import { useAuth } from '../lib/auth';
import { formatNumber, formatPercentage, formatDate } from '../lib/utils';
import apiClient from '../lib/api';

const Dashboard = () => {
  const [stats, setStats] = React.useState(null);
  const [loading, setLoading] = React.useState(true);
  const [error, setError] = React.useState('');
  const { user, isOperator } = useAuth();

  React.useEffect(() => {
    const fetchStats = async () => {
      if (!isOperator()) {
        setLoading(false);
        return;
      }

      try {
        const response = await apiClient.getDashboardStats(30);
        setStats(response);
      } catch (error) {
        setError('فشل في تحميل الإحصائيات');
        console.error('Error fetching stats:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchStats();
  }, [isOperator]);

  if (loading) {
    return (
      <div className="space-y-6">
        <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
          {[...Array(4)].map((_, i) => (
            <Card key={i} className="animate-pulse">
              <CardContent className="p-6">
                <div className="h-4 bg-gray-200 rounded w-3/4 mb-2"></div>
                <div className="h-8 bg-gray-200 rounded w-1/2"></div>
              </CardContent>
            </Card>
          ))}
        </div>
      </div>
    );
  }

  if (!isOperator()) {
    return (
      <div className="text-center py-12">
        <Wifi className="mx-auto h-12 w-12 text-gray-400" />
        <h3 className="mt-2 text-sm font-semibold text-gray-900 dark:text-white">
          مرحباً بك في نظام إدارة شبكات Wi-Fi
        </h3>
        <p className="mt-1 text-sm text-gray-500 dark:text-gray-400">
          أهلاً وسهلاً {user?.full_name || user?.username}
        </p>
        <div className="mt-6">
          <Button>
            استكشاف النظام
          </Button>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="text-center py-12">
        <div className="text-red-500 mb-4">خطأ في تحميل البيانات</div>
        <Button onClick={() => window.location.reload()}>
          إعادة المحاولة
        </Button>
      </div>
    );
  }

  const statCards = [
    {
      title: 'إجمالي المستخدمين',
      value: formatNumber(stats?.general_stats?.total_users || 0),
      icon: Users,
      color: 'text-blue-600',
      bgColor: 'bg-blue-100 dark:bg-blue-900',
    },
    {
      title: 'إجمالي الكروت',
      value: formatNumber(stats?.general_stats?.total_vouchers || 0),
      icon: CreditCard,
      color: 'text-green-600',
      bgColor: 'bg-green-100 dark:bg-green-900',
    },
    {
      title: 'الكروت النشطة',
      value: formatNumber(stats?.general_stats?.active_vouchers || 0),
      icon: Activity,
      color: 'text-yellow-600',
      bgColor: 'bg-yellow-100 dark:bg-yellow-900',
    },
    {
      title: 'الجلسات النشطة',
      value: formatNumber(stats?.general_stats?.active_sessions || 0),
      icon: Wifi,
      color: 'text-purple-600',
      bgColor: 'bg-purple-100 dark:bg-purple-900',
    },
  ];

  return (
    <div className="space-y-6">
      {/* Welcome Section */}
      <div className="bg-gradient-to-r from-blue-600 to-purple-600 rounded-lg p-6 text-white">
        <h1 className="text-2xl font-bold mb-2">
          مرحباً، {user?.full_name || user?.username}
        </h1>
        <p className="text-blue-100">
          إليك نظرة عامة على أداء شبكتك اليوم
        </p>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
        {statCards.map((stat, index) => (
          <Card key={index}>
            <CardContent className="p-6">
              <div className="flex items-center">
                <div className={`p-2 rounded-lg ${stat.bgColor}`}>
                  <stat.icon className={`h-6 w-6 ${stat.color}`} />
                </div>
                <div className="mr-4">
                  <p className="text-sm font-medium text-gray-600 dark:text-gray-400">
                    {stat.title}
                  </p>
                  <p className="text-2xl font-bold text-gray-900 dark:text-white">
                    {stat.value}
                  </p>
                </div>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      {/* Usage Statistics */}
      <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
        {/* Voucher Usage */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center">
              <CreditCard className="h-5 w-5 ml-2" />
              استخدام الكروت
            </CardTitle>
            <CardDescription>
              نسبة الكروت المستخدمة من إجمالي الكروت
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <span className="text-sm text-gray-600 dark:text-gray-400">
                  الكروت المستخدمة
                </span>
                <Badge variant="secondary">
                  {formatNumber(stats?.general_stats?.used_vouchers || 0)}
                </Badge>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-sm text-gray-600 dark:text-gray-400">
                  الكروت النشطة
                </span>
                <Badge variant="outline">
                  {formatNumber(stats?.general_stats?.active_vouchers || 0)}
                </Badge>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-sm text-gray-600 dark:text-gray-400">
                  نسبة الاستخدام
                </span>
                <div className="flex items-center">
                  {stats?.general_stats?.voucher_usage_percentage > 50 ? (
                    <TrendingUp className="h-4 w-4 text-green-500 ml-1" />
                  ) : (
                    <TrendingDown className="h-4 w-4 text-red-500 ml-1" />
                  )}
                  <span className="font-semibold">
                    {formatPercentage(
                      stats?.general_stats?.used_vouchers || 0,
                      stats?.general_stats?.total_vouchers || 1
                    )}
                  </span>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Recent Activity */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center">
              <Clock className="h-5 w-5 ml-2" />
              النشاط الأخير (30 يوم)
            </CardTitle>
            <CardDescription>
              إحصائيات الاستخدام في الفترة الأخيرة
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <span className="text-sm text-gray-600 dark:text-gray-400">
                  جلسات جديدة
                </span>
                <Badge variant="secondary">
                  {formatNumber(stats?.period_stats?.recent_sessions || 0)}
                </Badge>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-sm text-gray-600 dark:text-gray-400">
                  كروت مستخدمة
                </span>
                <Badge variant="outline">
                  {formatNumber(stats?.period_stats?.recent_vouchers_used || 0)}
                </Badge>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-sm text-gray-600 dark:text-gray-400">
                  متوسط الجلسات اليومية
                </span>
                <span className="font-semibold">
                  {Math.round((stats?.period_stats?.recent_sessions || 0) / 30)}
                </span>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Charts */}
      {stats?.daily_stats && stats.daily_stats.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center">
              <BarChart3 className="h-5 w-5 ml-2" />
              الجلسات اليومية
            </CardTitle>
            <CardDescription>
              عدد الجلسات المسجلة يومياً خلال آخر 30 يوم
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="h-80">
              <ResponsiveContainer width="100%" height="100%">
                <LineChart data={stats.daily_stats}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis 
                    dataKey="date" 
                    tickFormatter={(value) => formatDate(value)}
                  />
                  <YAxis />
                  <Tooltip 
                    labelFormatter={(value) => formatDate(value)}
                    formatter={(value) => [formatNumber(value), 'الجلسات']}
                  />
                  <Line 
                    type="monotone" 
                    dataKey="sessions_count" 
                    stroke="#3b82f6" 
                    strokeWidth={2}
                    dot={{ fill: '#3b82f6' }}
                  />
                </LineChart>
              </ResponsiveContainer>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Popular Batches */}
      {stats?.popular_batches && stats.popular_batches.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle>الدفعات الأكثر استخداماً</CardTitle>
            <CardDescription>
              أكثر دفعات الكروت استخداماً
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {stats.popular_batches.slice(0, 5).map((batch, index) => (
                <div key={batch.batch_id} className="flex items-center justify-between p-3 bg-gray-50 dark:bg-gray-800 rounded-lg">
                  <div className="flex items-center">
                    <div className="flex items-center justify-center w-8 h-8 bg-blue-100 dark:bg-blue-900 rounded-full ml-3">
                      <span className="text-sm font-medium text-blue-600 dark:text-blue-400">
                        {index + 1}
                      </span>
                    </div>
                    <div>
                      <p className="font-medium text-gray-900 dark:text-white">
                        {batch.batch_name}
                      </p>
                      <p className="text-sm text-gray-500 dark:text-gray-400">
                        {formatNumber(batch.used_vouchers)} من {formatNumber(batch.total_vouchers)} كرت
                      </p>
                    </div>
                  </div>
                  <Badge variant="secondary">
                    {formatPercentage(batch.used_vouchers, batch.total_vouchers)}
                  </Badge>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
};

export default Dashboard;

