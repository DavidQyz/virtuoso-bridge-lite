nch18_Cdd_Cgg=csvread('tsmc018/nch18_Cdd_Cgg.csv',1,0);
nch18_Cgd_Cgg=csvread('tsmc018/nch18_Cgd_Cgg.csv',1,0);
nch18_ft=csvread('tsmc018/nch18_ft.csv',1,0);
nch18_gm_gds=csvread('tsmc018/nch18_gm_gds.csv',1,0);
nch18_gm_Id=csvread('tsmc018/nch18_gm_Id.csv',1,0);
nch18_Id_W=csvread('tsmc018/nch18_Id_W.csv',1,0);
nch18_Vdsat=csvread('tsmc018/nch18_Vdsat.csv',1,0);
nch18_Vgs_Vth=csvread('tsmc018/nch18_Vgs_Vth.csv',1,0);
Vds_nch18_gm_gds=csvread('tsmc018/Vds_nch18_gm_gds.csv',7,0); %Delete the first seven rows of data
Vds_nch18_gm_Id=csvread('tsmc018/Vds_nch18_gm_Id.csv',7,0);

pch18_Cdd_Cgg=csvread('tsmc018/pch18_Cdd_Cgg.csv',1,0);
pch18_Cgd_Cgg=csvread('tsmc018/pch18_Cgd_Cgg.csv',1,0);
pch18_ft=csvread('tsmc018/pch18_ft.csv',1,0);
pch18_gm_gds=csvread('tsmc018/pch18_gm_gds.csv',1,0);
pch18_gm_Id=csvread('tsmc018/pch18_gm_Id.csv',1,0);
pch18_Id_W=csvread('tsmc018/pch18_Id_W.csv',1,0);
pch18_Vdsat=csvread('tsmc018/pch18_Vdsat.csv',1,0);
pch18_Vgs_Vth=csvread('tsmc018/pch18_Vgs_Vth.csv',1,0);
Vds_pch18_gm_gds=csvread('tsmc018/Vds_pch18_gm_gds.csv',7,0); %Delete the first seven rows of data
Vds_pch18_gm_Id=csvread('tsmc018/Vds_pch18_gm_Id.csv',7,0);

for i = 1:95
    for j = 1:15
        NCH3_Cdd_Cgg(i,j)=nch18_Cdd_Cgg(i,j*2);
        NCH3_Cgd_Cgg(i,j)=nch18_Cgd_Cgg(i,j*2);
        NCH3_ft(i,j)=nch18_ft(i,j*2);
        NCH3_gm_gds(i,j)=nch18_gm_gds(i,j*2);
        NCH3_gm_Id(i,j)=nch18_gm_Id(i,j*2);
        NCH3_Id_W(i,j)=nch18_Id_W(i,j*2);
        NCH3_Vdsat(i,j)=nch18_Vdsat(i,j*2);
        NCH3_Vgs_Vth(i,j)=nch18_Vgs_Vth(i,j*2);
        
        PCH3_Cdd_Cgg(i,j)=pch18_Cdd_Cgg(i,j*2);
        PCH3_Cgd_Cgg(i,j)=pch18_Cgd_Cgg(i,j*2);
        PCH3_ft(i,j)=pch18_ft(i,j*2);
        PCH3_gm_gds(i,j)=pch18_gm_gds(i,j*2);
        PCH3_gm_Id(i,j)=pch18_gm_Id(i,j*2);
        PCH3_Id_W(i,j)=pch18_Id_W(i,j*2);
        PCH3_Vdsat(i,j)=-pch18_Vdsat(i,j*2);% Date Negation
        PCH3_Vgs_Vth(i,j)=pch18_Vgs_Vth(i,j*2); 
        
    end
end

for i = 1:25
    for j = 1:150
        Vds_NCH3_gm_Id(i,j)=Vds_nch18_gm_Id(i,j*2);
        Vds_NCH3_gm_gds(i,j)=Vds_nch18_gm_gds(i,j*2);

        Vds_PCH3_gm_Id(i,j)=Vds_pch18_gm_Id(i,j*2);
        Vds_PCH3_gm_gds(i,j)=Vds_pch18_gm_gds(i,j*2);
    end
end
save('MOS_GmId_Data.mat',...
    'NCH3_Cdd_Cgg','NCH3_Cgd_Cgg','NCH3_ft','NCH3_gm_gds','NCH3_gm_Id','NCH3_Id_W','NCH3_Vdsat','NCH3_Vgs_Vth',...
    'PCH3_Cdd_Cgg','PCH3_Cgd_Cgg','PCH3_ft','PCH3_gm_gds','PCH3_gm_Id','PCH3_Id_W','PCH3_Vdsat','PCH3_Vgs_Vth',...
    'Vds_NCH3_gm_gds','Vds_NCH3_gm_Id','Vds_PCH3_gm_gds','Vds_PCH3_gm_Id')
