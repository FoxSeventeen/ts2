#include<bits/stdc++.h>
using namespace std;
int main()
{
    int n;
    cin>>n;
    vector<int> a(n);
    for(int i=0;i<n;i++) cin>>a[i];
    int target;
    cin>>target;
    int left=0, right=n-1;
    bool found=false;
    while(left<=right)
    {
        int mid=left+(right-left)/2;
        if(a[mid]==target)
        {
            found=true;
            break;
        }
        else if(a[mid]<target)
        {
            left=mid+1;
        }
        else
        {
            right=mid-1;
        }
    }
    if(found) cout<<"Found"<<endl;
    else cout<<"Not Found"<<endl;
    return 0;
}