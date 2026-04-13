#include<stdio.h>
#include<stdlib.h>
void main(){
    int  f[50];
     for(int i=0;i<50;i++){
         f[i]=0;
     }
     printf("Enter how many Blocks already allocated:");
     int h;
     int a;
     scanf("%d",&h);
     printf("enter the allocated blocks number:\n");
     
     for(int i=0;i<h;i++){
         scanf("%d",&a);
         f[a]=1;
     }
     x:
     printf("Enter the number length and then startin point:\n");
     int start,len;
     scanf(" %d %d",&len,&start);
     
     
     if(f[start]==0){
         for(int i=0;i<(start+len);i++){
             if (f[i]==0) {
             f[i]=1;
             printf("%d--->",i);
         }
         else  
         len++;
     }
     printf("\n");
     }
     else printf("%d is already allocated\n",start);
     int k;
     
     printf("do u want allocation (yes=1,no=1)\n");
     scanf("%d",&k);
     if(k==1){
     goto x;
     }
     else {
         exit(0);
     }
    
     
     
     
    
}
