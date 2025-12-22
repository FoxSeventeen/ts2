#include<bits/stdc++.h>
using namespace std;
int a[100005];
void quick_sort(int left,int right)
{
    if(left>=right) return;
    int pivot=a[left];//选取基准元素
    int i=left,j=right;//左右指针
    while(i<j)
    {
        while(i<j&&a[j]>=pivot) j--;
        if(i<j) a[i++]=a[j];//从右向左找比基准小的元素
        while(i<j&&a[i]<=pivot) i++;
        if(i<j) a[j--]=a[i];//从左向右找比基准大的元素
    }
    a[i]=pivot;//将基准元素放到正确位置
    quick_sort(left,i-1);//递归排序左子数组
    quick_sort(i+1,right);//递归排序右子数组
};
int main()
{
    int n;
    cin>>n;
    vector<int> a(n);
    for(int i=0;i<n;i++) cin>>a[i];
    sort(a.begin(),a.end());
    for(int i=0;i<n;i++) cout<<a[i]<<" ";
    return 0;   
}