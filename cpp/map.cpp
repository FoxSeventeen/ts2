#include<bits/stdc++.h>
using namespace std;
class edge
{
    int n,st,a[101][101];
    private:
    void dfs(int x)//内置dfs函数
    {
        for(int i=1;i<=n;i++)
        {
            if(a[x][i]==1)
            {
                a[x][i]=0;
                cout<<x<<" "<<i<<endl;
                dfs(i);
            }
        }
    }
    public:
    void add(int i,int j)
    {
        a[i][j]=1;
    }
    void display()//输出路径函数
    {
        dfs(st);
    }
    void edge_init(int nn,int s)//初始化函数
    {
        n=nn;
        st=s;
        for(int i=1;i<=n;i++)
        {
            for(int j=1;j<=n;j++)
            {
                a[i][j]=0;
            }
        }
    }
};
int main()
{
    edge e;//创建edge类对象 每一个对象对应了一个快递的递送路径数据
    int n,m,s,u,v;
    cin>>n>>m>>s;//输入点数，边数，起始点
    e.edge_init(n,s);//初始化
    for(int i=1;i<=m;i++)//输入边
    {
        cin>>u>>v;
        e.add(u,v);
    }
    e.display();//输出路径
    return 0;
}