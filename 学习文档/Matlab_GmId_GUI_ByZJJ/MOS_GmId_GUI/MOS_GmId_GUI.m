function varargout = MOS_GmId_GUI(varargin)


% MOS_GmId_GUI MATLAB code for MOS_GmId_GUI.fig
%      MOS_GmId_GUI, by itself, creates a new MOS_GmId_GUI or raises the existing
%      singleton*.
%
%      H = MOS_GmId_GUI returns the handle to a new MOS_GmId_GUI or the handle to
%      the existing singleton*.
%
%      MOS_GmId_GUI('CALLBACK',hObject,eventData,handles,...) calls the local
%      function named CALLBACK in MOS_GmId_GUI.M with the given input arguments.
%
%      MOS_GmId_GUI('Property','Value',...) creates a new MOS_GmId_GUI or raises the
%      existing singleton*.  Starting from the left, property value pairs are
%      applied to the GUI before MOS_GmId_GUI_OpeningFcn gets called.  An
%      unrecognized property name or invalid value makes property application
%      stop.  All inputs are passed to MOS_GmId_GUI_OpeningFcn via varargin.
%
%      *See GUI Options on GUIDE's Tools menu.  Choose "GUI allows only one
%      instance to run (singleton)".
%
% See also: GUIDE, GUIDATA, GUIHANDLES

% Edit the above text to modify the response to help MOS_GmId_GUI

% Last Modified by GUIDE v2.5 11-Aug-2013 22:07:47

% Begin initialization code - DO NOT EDIT
gui_Singleton = 1;
gui_State = struct('gui_Name',       mfilename, ...
                   'gui_Singleton',  gui_Singleton, ...
                   'gui_OpeningFcn', @MOS_GmId_GUI_OpeningFcn, ...
                   'gui_OutputFcn',  @MOS_GmId_GUI_OutputFcn, ...
                   'gui_LayoutFcn',  [] , ...
                   'gui_Callback',   []);
if nargin && ischar(varargin{1})
    gui_State.gui_Callback = str2func(varargin{1});
end

if nargout
    [varargout{1:nargout}] = gui_mainfcn(gui_State, varargin{:});
else
    gui_mainfcn(gui_State, varargin{:});
end
% End initialization code - DO NOT EDIT


% --- Executes just before MOS_GmId_GUI is made visible.
function MOS_GmId_GUI_OpeningFcn(hObject, eventdata, handles, varargin)
% This function has no output args, see OutputFcn.
% hObject    handle to figure
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)
% varargin   command line arguments to MOS_GmId_GUI (see VARARGIN)

% Choose default command line output for MOS_GmId_GUI
handles.output = hObject;

% Update handles structure
guidata(hObject, handles);

% UIWAIT makes MOS_GmId_GUI wait for user response (see UIRESUME)
% uiwait(handles.figure1);


% --- Outputs from this function are returned to the command line.
function varargout = MOS_GmId_GUI_OutputFcn(hObject, eventdata, handles) 
% varargout  cell array for returning output args (see VARARGOUT);
% hObject    handle to figure
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)

% Get default command line output from handles structure
varargout{1} = handles.output;


% --- Executes on selection change in popupmenu_ll.
function popupmenu_ll_Callback(hObject, eventdata, handles)
% hObject    handle to popupmenu_ll (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)

% Hints: contents = cellstr(get(hObject,'String')) returns popupmenu_ll contents as cell array
%        contents{get(hObject,'Value')} returns selected item from popupmenu_ll


% --- Executes during object creation, after setting all properties.
function popupmenu_ll_CreateFcn(hObject, eventdata, handles)
% hObject    handle to popupmenu_ll (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    empty - handles not created until after all CreateFcns called

% Hint: popupmenu controls usually have a white background on Windows.
%       See ISPC and COMPUTER.
if ispc && isequal(get(hObject,'BackgroundColor'), get(0,'defaultUicontrolBackgroundColor'))
    set(hObject,'BackgroundColor','white');
end
L_values = [0.18 0.2:0.1:1 1.2:0.2:2.4];  % 与你的数据文件一致
L_strings = cell(1, length(L_values));
for i = 1:length(L_values)
    L_strings{i} = sprintf('%.2fum', L_values(i));
end
set(hObject, 'String', L_strings);
set(hObject, 'Value', 1);  % 默认选择第一个 (0.18um)


function edit_nch3_gmId_Callback(hObject, eventdata, handles)
% hObject    handle to edit_nch3_gmId (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)

% Hints: get(hObject,'String') returns contents of edit_nch3_gmId as text
%        str2double(get(hObject,'String')) returns contents of edit_nch3_gmId as a double


% --- Executes during object creation, after setting all properties.
function edit_nch3_gmId_CreateFcn(hObject, eventdata, handles)
% hObject    handle to edit_nch3_gmId (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    empty - handles not created until after all CreateFcns called

% Hint: edit controls usually have a white background on Windows.
%       See ISPC and COMPUTER.
if ispc && isequal(get(hObject,'BackgroundColor'), get(0,'defaultUicontrolBackgroundColor'))
    set(hObject,'BackgroundColor','white');
end



function edit_nch3_gmId_else_Callback(hObject, eventdata, handles)
% hObject    handle to edit_nch3_gmId_else (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)

% Hints: get(hObject,'String') returns contents of edit_nch3_gmId_else as text
%        str2double(get(hObject,'String')) returns contents of edit_nch3_gmId_else as a double


% --- Executes during object creation, after setting all properties.
function edit_nch3_gmId_else_CreateFcn(hObject, eventdata, handles)
% hObject    handle to edit_nch3_gmId_else (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    empty - handles not created until after all CreateFcns called

% Hint: edit controls usually have a white background on Windows.
%       See ISPC and COMPUTER.
if ispc && isequal(get(hObject,'BackgroundColor'), get(0,'defaultUicontrolBackgroundColor'))
    set(hObject,'BackgroundColor','white');
end


% --- Executes on button press in pushbutton_nch3_gmId.
function pushbutton_nch3_gmId_Callback(hObject, eventdata, handles)
% hObject    handle to pushbutton_nch3_gmId (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)

ll=get(handles.popupmenu_ll,'Value');
gm_Id=str2double(get(handles.edit_nch3_gmId,'String'));
global data_gmId;
gm_Id_max=max(data_gmId.NCH3_gm_Id(:,ll));
gm_Id_min=min(data_gmId.NCH3_gm_Id(:,ll));

if gm_Id>=gm_Id_min && gm_Id<=gm_Id_max
%1.����Id/W
x=data_gmId.NCH3_gm_Id(:,ll);
y=data_gmId.NCH3_Id_W(:,ll);
Id_W=interp1(x,y,gm_Id);
%2.����Vdsat
x=data_gmId.NCH3_gm_Id(:,ll);
y=data_gmId.NCH3_Vdsat(:,ll);
Vdsat=interp1(x,y,gm_Id);
%3.����Vgs-Vth
x=data_gmId.NCH3_gm_Id(:,ll);
y=data_gmId.NCH3_Vgs_Vth(:,ll);
Vgs_Vth=interp1(x,y,gm_Id);
%4.����ft
x=data_gmId.NCH3_gm_Id(:,ll);
y=data_gmId.NCH3_ft(:,ll);
y=y/10^9;
ft=interp1(x,y,gm_Id);
%5.����gm/gds
x=data_gmId.NCH3_gm_Id(:,ll);
y=data_gmId.NCH3_gm_gds(:,ll);
gm_gds=interp1(x,y,gm_Id);
%6.����Cdd/Cgg
x=data_gmId.NCH3_gm_Id(:,ll);
y=data_gmId.NCH3_Cdd_Cgg(:,ll);
Cdd_Cgg=interp1(x,y,gm_Id);
%7.����Cgd/Cgg
x=data_gmId.NCH3_gm_Id(:,ll);
y=data_gmId.NCH3_Cgd_Cgg(:,ll);
Cgd_Cgg=interp1(x,y,gm_Id);

outstr=['Id/W=',num2str(Id_W),'A/m',' ; ','Vdsat=',num2str(Vdsat),'V',10,'Vgs-Vth=',num2str(Vgs_Vth),'V',' ; ','ft=',num2str(ft),'GHz',10,'gm/gds=',num2str(gm_gds),10,'Cdd/Cgg=',num2str(Cdd_Cgg),' ; ','Cgd/Cgg=',num2str(Cgd_Cgg)];
set(handles.edit_nch3_gmId_else,'String',outstr);
else
   set(handles.edit_nch3_gmId_else,'String','The input gm/Id is out of range!'); 
end


% --- Executes on button press in pushbutton_loaddata.
function pushbutton_loaddata_Callback(hObject, eventdata, handles)
% hObject    handle to pushbutton_loaddata (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)
global data_gmId;

data_gmId=load('MOS_GmId_Data.mat');

dataok=isstruct(data_gmId);

if dataok==1
    set(handles.edit_dataok,'String','The data of MOS have been loaded successfully!');
else
    set(handles.edit_dataok,'String','Problems occur during data loading!');
end


    
function edit_dataok_Callback(hObject, eventdata, handles)
% hObject    handle to edit_dataok (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)

% Hints: get(hObject,'String') returns contents of edit_dataok as text
%        str2double(get(hObject,'String')) returns contents of edit_dataok as a double


% --- Executes during object creation, after setting all properties.
function edit_dataok_CreateFcn(hObject, eventdata, handles)
% hObject    handle to edit_dataok (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    empty - handles not created until after all CreateFcns called

% Hint: edit controls usually have a white background on Windows.
%       See ISPC and COMPUTER.
if ispc && isequal(get(hObject,'BackgroundColor'), get(0,'defaultUicontrolBackgroundColor'))
    set(hObject,'BackgroundColor','white');
end



function edit_nch3_Vds_gmId_Callback(hObject, eventdata, handles)
% hObject    handle to edit_nch3_Vds_gmId (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)

% Hints: get(hObject,'String') returns contents of edit_nch3_Vds_gmId as text
%        str2double(get(hObject,'String')) returns contents of edit_nch3_Vds_gmId as a double


% --- Executes during object creation, after setting all properties.
function edit_nch3_Vds_gmId_CreateFcn(hObject, eventdata, handles)
% hObject    handle to edit_nch3_Vds_gmId (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    empty - handles not created until after all CreateFcns called

% Hint: edit controls usually have a white background on Windows.
%       See ISPC and COMPUTER.
if ispc && isequal(get(hObject,'BackgroundColor'), get(0,'defaultUicontrolBackgroundColor'))
    set(hObject,'BackgroundColor','white');
end


% --- Executes on button press in pushbutton_nch3_Vds.
function pushbutton_nch3_Vds_Callback(hObject, eventdata, handles)
% hObject    handle to pushbutton_nch3_Vds (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)

ll=get(handles.popupmenu_ll,'Value');
vds=get(handles.popupmenu_nch3_Vds,'Value');
gm_Id=str2double(get(handles.edit_nch3_Vds_gmId,'String'));

global data_gmId;
x=data_gmId.Vds_NCH3_gm_Id(:,(ll-1)*10+vds);
y=data_gmId.Vds_NCH3_gm_gds(:,(ll-1)*10+vds);
gm_Id_max=max(x);
gm_Id_min=min(x);

if gm_Id<=gm_Id_max && gm_Id>=gm_Id_min
%����gm/gds
   gm_gds=interp1(x,y,gm_Id);
   outstr=['gm/gds=',num2str(gm_gds)];
   set(handles.edit_nch3_Vds_gmgds,'String',outstr);
else
   set(handles.edit_nch3_Vds_gmgds,'String','The input gm/Id is out of range!'); 
end






function edit_nch3_Vdsat_Callback(hObject, eventdata, handles)
% hObject    handle to edit_nch3_Vdsat (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)

% Hints: get(hObject,'String') returns contents of edit_nch3_Vdsat as text
%        str2double(get(hObject,'String')) returns contents of edit_nch3_Vdsat as a double


% --- Executes during object creation, after setting all properties.
function edit_nch3_Vdsat_CreateFcn(hObject, eventdata, handles)
% hObject    handle to edit_nch3_Vdsat (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    empty - handles not created until after all CreateFcns called

% Hint: edit controls usually have a white background on Windows.
%       See ISPC and COMPUTER.
if ispc && isequal(get(hObject,'BackgroundColor'), get(0,'defaultUicontrolBackgroundColor'))
    set(hObject,'BackgroundColor','white');
end



function edit_nch3_Vdsat_else_Callback(hObject, eventdata, handles)
% hObject    handle to edit_nch3_Vdsat_else (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)

% Hints: get(hObject,'String') returns contents of edit_nch3_Vdsat_else as text
%        str2double(get(hObject,'String')) returns contents of edit_nch3_Vdsat_else as a double


% --- Executes during object creation, after setting all properties.
function edit_nch3_Vdsat_else_CreateFcn(hObject, eventdata, handles)
% hObject    handle to edit_nch3_Vdsat_else (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    empty - handles not created until after all CreateFcns called

% Hint: edit controls usually have a white background on Windows.
%       See ISPC and COMPUTER.
if ispc && isequal(get(hObject,'BackgroundColor'), get(0,'defaultUicontrolBackgroundColor'))
    set(hObject,'BackgroundColor','white');
end


% --- Executes on button press in pushbutton_nch3_Vdsat.
function pushbutton_nch3_Vdsat_Callback(hObject, eventdata, handles)
% hObject    handle to pushbutton_nch3_Vdsat (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)
ll=get(handles.popupmenu_ll,'Value');
Vdsat=str2double(get(handles.edit_nch3_Vdsat,'String'));
global data_gmId;
Vdsat_max=max(data_gmId.NCH3_Vdsat(:,ll));
Vdsat_min=min(data_gmId.NCH3_Vdsat(:,ll));

if Vdsat>=Vdsat_min && Vdsat<=Vdsat_max
%1.����gm/Id
x=data_gmId.NCH3_Vdsat(:,ll);
y=data_gmId.NCH3_gm_Id(:,ll);
gm_Id=interp1(x,y,Vdsat);
%2.����Id/W
x=data_gmId.NCH3_gm_Id(:,ll);
y=data_gmId.NCH3_Id_W(:,ll);
Id_W=interp1(x,y,gm_Id);
%3.����Vgs-Vth
x=data_gmId.NCH3_gm_Id(:,ll);
y=data_gmId.NCH3_Vgs_Vth(:,ll);
Vgs_Vth=interp1(x,y,gm_Id);
%4.����ft
x=data_gmId.NCH3_gm_Id(:,ll);
y=data_gmId.NCH3_ft(:,ll);
y=y/10^9;
ft=interp1(x,y,gm_Id);
%5.����gm/gds
x=data_gmId.NCH3_gm_Id(:,ll);
y=data_gmId.NCH3_gm_gds(:,ll);
gm_gds=interp1(x,y,gm_Id);
%6.����Cdd/Cgg
x=data_gmId.NCH3_gm_Id(:,ll);
y=data_gmId.NCH3_Cdd_Cgg(:,ll);
Cdd_Cgg=interp1(x,y,gm_Id);
%7.����Cgd/Cgg
x=data_gmId.NCH3_gm_Id(:,ll);
y=data_gmId.NCH3_Cgd_Cgg(:,ll);
Cgd_Cgg=interp1(x,y,gm_Id);

outstr=['gm/Id=',num2str(gm_Id),'S/A',' ; ','Id/W=',num2str(Id_W),'A/m',10,'Vgs-Vth=',num2str(Vgs_Vth),'V',' ; ','ft=',num2str(ft),'GHz',10,'gm/gds=',num2str(gm_gds),10,'Cdd/Cgg=',num2str(Cdd_Cgg),' ; ','Cgd/Cgg=',num2str(Cgd_Cgg)];
set(handles.edit_nch3_Vdsat_else,'String',outstr);
else
   set(handles.edit_nch3_Vdsat_else,'String','The input Vdsat is out of range!'); 
end


function edit_nch3_Vds_gmgds_Callback(hObject, eventdata, handles)
% hObject    handle to edit_nch3_Vds_gmgds (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)

% Hints: get(hObject,'String') returns contents of edit_nch3_Vds_gmgds as text
%        str2double(get(hObject,'String')) returns contents of edit_nch3_Vds_gmgds as a double


% --- Executes during object creation, after setting all properties.
function edit_nch3_Vds_gmgds_CreateFcn(hObject, eventdata, handles)
% hObject    handle to edit_nch3_Vds_gmgds (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    empty - handles not created until after all CreateFcns called

% Hint: edit controls usually have a white background on Windows.
%       See ISPC and COMPUTER.
if ispc && isequal(get(hObject,'BackgroundColor'), get(0,'defaultUicontrolBackgroundColor'))
    set(hObject,'BackgroundColor','white');
end


% --- Executes on selection change in popupmenu_nch3_Vds.
function popupmenu_nch3_Vds_Callback(hObject, eventdata, handles)
% hObject    handle to popupmenu_nch3_Vds (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)

% Hints: contents = cellstr(get(hObject,'String')) returns popupmenu_nch3_Vds contents as cell array
%        contents{get(hObject,'Value')} returns selected item from popupmenu_nch3_Vds


% --- Executes during object creation, after setting all properties.
function popupmenu_nch3_Vds_CreateFcn(hObject, eventdata, handles)
% hObject    handle to popupmenu_nch3_Vds (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    empty - handles not created until after all CreateFcns called

% Hint: popupmenu controls usually have a white background on Windows.
%       See ISPC and COMPUTER.
if ispc && isequal(get(hObject,'BackgroundColor'), get(0,'defaultUicontrolBackgroundColor'))
    set(hObject,'BackgroundColor','white');
end



function edit_pch3_gmId_Callback(hObject, eventdata, handles)
% hObject    handle to edit_pch3_gmId (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)

% Hints: get(hObject,'String') returns contents of edit_pch3_gmId as text
%        str2double(get(hObject,'String')) returns contents of edit_pch3_gmId as a double


% --- Executes during object creation, after setting all properties.
function edit_pch3_gmId_CreateFcn(hObject, eventdata, handles)
% hObject    handle to edit_pch3_gmId (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    empty - handles not created until after all CreateFcns called

% Hint: edit controls usually have a white background on Windows.
%       See ISPC and COMPUTER.
if ispc && isequal(get(hObject,'BackgroundColor'), get(0,'defaultUicontrolBackgroundColor'))
    set(hObject,'BackgroundColor','white');
end



function edit_pch3_gmId_else_Callback(hObject, eventdata, handles)
% hObject    handle to edit_pch3_gmId_else (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)

% Hints: get(hObject,'String') returns contents of edit_pch3_gmId_else as text
%        str2double(get(hObject,'String')) returns contents of edit_pch3_gmId_else as a double


% --- Executes during object creation, after setting all properties.
function edit_pch3_gmId_else_CreateFcn(hObject, eventdata, handles)
% hObject    handle to edit_pch3_gmId_else (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    empty - handles not created until after all CreateFcns called

% Hint: edit controls usually have a white background on Windows.
%       See ISPC and COMPUTER.
if ispc && isequal(get(hObject,'BackgroundColor'), get(0,'defaultUicontrolBackgroundColor'))
    set(hObject,'BackgroundColor','white');
end


% --- Executes on button press in pushbutton_pch3_gmId.
function pushbutton_pch3_gmId_Callback(hObject, eventdata, handles)
% hObject    handle to pushbutton_pch3_gmId (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)

ll=get(handles.popupmenu_ll,'Value');
gm_Id=str2double(get(handles.edit_pch3_gmId,'String'));
global data_gmId;
gm_Id_max=max(data_gmId.PCH3_gm_Id(:,ll));
gm_Id_min=min(data_gmId.PCH3_gm_Id(:,ll));

if gm_Id>=gm_Id_min && gm_Id<=gm_Id_max
%1.����Id/W
x=data_gmId.PCH3_gm_Id(:,ll);
y=data_gmId.PCH3_Id_W(:,ll);
Id_W=interp1(x,y,gm_Id);
%2.����Vdsat
x=data_gmId.PCH3_gm_Id(:,ll);
y=data_gmId.PCH3_Vdsat(:,ll);
Vdsat=interp1(x,y,gm_Id);
%3.����Vgs-Vth
x=data_gmId.PCH3_gm_Id(:,ll);
y=data_gmId.PCH3_Vgs_Vth(:,ll);
Vgs_Vth=interp1(x,y,gm_Id);
%4.����ft
x=data_gmId.PCH3_gm_Id(:,ll);
y=data_gmId.PCH3_ft(:,ll);
y=y/10^9;
ft=interp1(x,y,gm_Id);
%5.����gm/gds
x=data_gmId.PCH3_gm_Id(:,ll);
y=data_gmId.PCH3_gm_gds(:,ll);
gm_gds=interp1(x,y,gm_Id);
%6.����Cdd/Cgg
x=data_gmId.PCH3_gm_Id(:,ll);
y=data_gmId.PCH3_Cdd_Cgg(:,ll);
Cdd_Cgg=interp1(x,y,gm_Id);
%7.����Cgd/Cgg
x=data_gmId.PCH3_gm_Id(:,ll);
y=data_gmId.PCH3_Cgd_Cgg(:,ll);
Cgd_Cgg=interp1(x,y,gm_Id);

outstr=['Id/W=',num2str(Id_W),'A/m',' ; ','Vdsat=',num2str(Vdsat),'V',10,'Vgs-Vth=',num2str(Vgs_Vth),'V',' ; ','ft=',num2str(ft),'GHz',10,'gm/gds=',num2str(gm_gds),10,'Cdd/Cgg=',num2str(Cdd_Cgg),' ; ','Cgd/Cgg=',num2str(Cgd_Cgg)];
set(handles.edit_pch3_gmId_else,'String',outstr);
else
   set(handles.edit_pch3_gmId_else,'String','The input gm/Id is out of range!'); 
end


function edit_pch3_Vds_gmId_Callback(hObject, eventdata, handles)
% hObject    handle to edit_pch3_Vds_gmId (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)

% Hints: get(hObject,'String') returns contents of edit_pch3_Vds_gmId as text
%        str2double(get(hObject,'String')) returns contents of edit_pch3_Vds_gmId as a double


% --- Executes during object creation, after setting all properties.
function edit_pch3_Vds_gmId_CreateFcn(hObject, eventdata, handles)
% hObject    handle to edit_pch3_Vds_gmId (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    empty - handles not created until after all CreateFcns called

% Hint: edit controls usually have a white background on Windows.
%       See ISPC and COMPUTER.
if ispc && isequal(get(hObject,'BackgroundColor'), get(0,'defaultUicontrolBackgroundColor'))
    set(hObject,'BackgroundColor','white');
end


% --- Executes on button press in pushbutton_pch3_Vds.
function pushbutton_pch3_Vds_Callback(hObject, eventdata, handles)
% hObject    handle to pushbutton_pch3_Vds (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)

ll=get(handles.popupmenu_ll,'Value');
vds=get(handles.popupmenu_pch3_Vds,'Value');
gm_Id=str2double(get(handles.edit_pch3_Vds_gmId,'String'));

global data_gmId;
x=data_gmId.Vds_PCH3_gm_Id(:,(ll-1)*10+vds);
y=data_gmId.Vds_PCH3_gm_gds(:,(ll-1)*10+vds);
gm_Id_max=max(x);
gm_Id_min=min(x);

if gm_Id<=gm_Id_max && gm_Id>=gm_Id_min
%����gm/gds
   gm_gds=interp1(x,y,gm_Id);
   outstr=['gm/gds=',num2str(gm_gds)];
   set(handles.edit_pch3_Vds_gmgds,'String',outstr);
else
   set(handles.edit_pch3_Vds_gmgds,'String','The input gm/Id is out of range!'); 
end


function edit_pch3_Vdsat_Callback(hObject, eventdata, handles)
% hObject    handle to edit_pch3_Vdsat (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)

% Hints: get(hObject,'String') returns contents of edit_pch3_Vdsat as text
%        str2double(get(hObject,'String')) returns contents of edit_pch3_Vdsat as a double


% --- Executes during object creation, after setting all properties.
function edit_pch3_Vdsat_CreateFcn(hObject, eventdata, handles)
% hObject    handle to edit_pch3_Vdsat (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    empty - handles not created until after all CreateFcns called

% Hint: edit controls usually have a white background on Windows.
%       See ISPC and COMPUTER.
if ispc && isequal(get(hObject,'BackgroundColor'), get(0,'defaultUicontrolBackgroundColor'))
    set(hObject,'BackgroundColor','white');
end



function edit_pch3_Vdsat_else_Callback(hObject, eventdata, handles)
% hObject    handle to edit_pch3_Vdsat_else (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)

% Hints: get(hObject,'String') returns contents of edit_pch3_Vdsat_else as text
%        str2double(get(hObject,'String')) returns contents of edit_pch3_Vdsat_else as a double


% --- Executes during object creation, after setting all properties.
function edit_pch3_Vdsat_else_CreateFcn(hObject, eventdata, handles)
% hObject    handle to edit_pch3_Vdsat_else (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    empty - handles not created until after all CreateFcns called

% Hint: edit controls usually have a white background on Windows.
%       See ISPC and COMPUTER.
if ispc && isequal(get(hObject,'BackgroundColor'), get(0,'defaultUicontrolBackgroundColor'))
    set(hObject,'BackgroundColor','white');
end


% --- Executes on button press in pushbutton_pch3_Vdsat.
function pushbutton_pch3_Vdsat_Callback(hObject, eventdata, handles)
% hObject    handle to pushbutton_pch3_Vdsat (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)
ll=get(handles.popupmenu_ll,'Value');
Vdsat=str2double(get(handles.edit_pch3_Vdsat,'String'));
global data_gmId;
Vdsat_max=max(data_gmId.PCH3_Vdsat(:,ll));
Vdsat_min=min(data_gmId.PCH3_Vdsat(:,ll));

if Vdsat>=Vdsat_min && Vdsat<=Vdsat_max
%1.����gm/Id
x=data_gmId.PCH3_Vdsat(:,ll);
y=data_gmId.PCH3_gm_Id(:,ll);
gm_Id=interp1(x,y,Vdsat);
%2.����Id/W
x=data_gmId.PCH3_gm_Id(:,ll);
y=data_gmId.PCH3_Id_W(:,ll);
Id_W=interp1(x,y,gm_Id);
%3.����Vgs-Vth
x=data_gmId.PCH3_gm_Id(:,ll);
y=data_gmId.PCH3_Vgs_Vth(:,ll);
Vgs_Vth=interp1(x,y,gm_Id);
%4.����ft
x=data_gmId.PCH3_gm_Id(:,ll);
y=data_gmId.PCH3_ft(:,ll);
y=y/10^9;
ft=interp1(x,y,gm_Id);
%5.����gm/gds
x=data_gmId.PCH3_gm_Id(:,ll);
y=data_gmId.PCH3_gm_gds(:,ll);
gm_gds=interp1(x,y,gm_Id);
%6.����Cdd/Cgg
x=data_gmId.PCH3_gm_Id(:,ll);
y=data_gmId.PCH3_Cdd_Cgg(:,ll);
Cdd_Cgg=interp1(x,y,gm_Id);
%7.����Cgd/Cgg
x=data_gmId.PCH3_gm_Id(:,ll);
y=data_gmId.PCH3_Cgd_Cgg(:,ll);
Cgd_Cgg=interp1(x,y,gm_Id);

outstr=['gm/Id=',num2str(gm_Id),'S/A',' ; ','Id/W=',num2str(Id_W),'A/m',10,'Vgs-Vth=',num2str(Vgs_Vth),'V',' ; ','ft=',num2str(ft),'GHz',10,'gm/gds=',num2str(gm_gds),10,'Cdd/Cgg=',num2str(Cdd_Cgg),' ; ','Cgd/Cgg=',num2str(Cgd_Cgg)];
set(handles.edit_pch3_Vdsat_else,'String',outstr);
else
   set(handles.edit_pch3_Vdsat_else,'String','The input Vdsat is out of range!'); 
end

% --- Executes on selection change in popupmenu_pch3_Vds.
function popupmenu_pch3_Vds_Callback(hObject, eventdata, handles)
% hObject    handle to popupmenu_pch3_Vds (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)

% Hints: contents = cellstr(get(hObject,'String')) returns popupmenu_pch3_Vds contents as cell array
%        contents{get(hObject,'Value')} returns selected item from popupmenu_pch3_Vds


% --- Executes during object creation, after setting all properties.
function popupmenu_pch3_Vds_CreateFcn(hObject, eventdata, handles)
% hObject    handle to popupmenu_pch3_Vds (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    empty - handles not created until after all CreateFcns called

% Hint: popupmenu controls usually have a white background on Windows.
%       See ISPC and COMPUTER.
if ispc && isequal(get(hObject,'BackgroundColor'), get(0,'defaultUicontrolBackgroundColor'))
    set(hObject,'BackgroundColor','white');
end



function edit_pch3_Vds_gmgds_Callback(hObject, eventdata, handles)
% hObject    handle to edit_pch3_Vds_gmgds (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)

% Hints: get(hObject,'String') returns contents of edit_pch3_Vds_gmgds as text
%        str2double(get(hObject,'String')) returns contents of edit_pch3_Vds_gmgds as a double


% --- Executes during object creation, after setting all properties.
function edit_pch3_Vds_gmgds_CreateFcn(hObject, eventdata, handles)
% hObject    handle to edit_pch3_Vds_gmgds (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    empty - handles not created until after all CreateFcns called

% Hint: edit controls usually have a white background on Windows.
%       See ISPC and COMPUTER.
if ispc && isequal(get(hObject,'BackgroundColor'), get(0,'defaultUicontrolBackgroundColor'))
    set(hObject,'BackgroundColor','white');
end


% --- Executes on selection change in popupmenu_gmId_draw.
function popupmenu_gmId_draw_Callback(hObject, eventdata, handles)
% hObject    handle to popupmenu_gmId_draw (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)

% Hints: contents = cellstr(get(hObject,'String')) returns popupmenu_gmId_draw contents as cell array
%        contents{get(hObject,'Value')} returns selected item from popupmenu_gmId_draw


% --- Executes during object creation, after setting all properties.
function popupmenu_gmId_draw_CreateFcn(hObject, eventdata, handles)
% hObject    handle to popupmenu_gmId_draw (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    empty - handles not created until after all CreateFcns called

% Hint: popupmenu controls usually have a white background on Windows.
%       See ISPC and COMPUTER.
if ispc && isequal(get(hObject,'BackgroundColor'), get(0,'defaultUicontrolBackgroundColor'))
    set(hObject,'BackgroundColor','white');
end


% --- Executes on button press in pushbutton_draw_gmId.
function pushbutton_draw_gmId_Callback(hObject, eventdata, handles)
% hObject    handle to pushbutton_draw_gmId (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)

draw_index=get(handles.popupmenu_gmId_draw,'Value');

lineshape=cell(1,15);
lineshape(1)={'-b'};
lineshape(2)={'-r'};
lineshape(3)={'-g'};
lineshape(4)={'-m'};
lineshape(5)={'-k'};

lineshape(6)={':.b'};
lineshape(7)={':.r'};
lineshape(8)={':.g'};
lineshape(9)={':.m'};
lineshape(10)={':.k'};

lineshape(11)={'--b'};
lineshape(12)={'--r'};
lineshape(13)={'--g'};
lineshape(14)={'--m'};
lineshape(15)={'--k'};

L=[0.18 0.2:0.1:1 1.2:0.2:2.4];
global data_gmId;

switch draw_index

    case 1
%Id/W - gm/Id
figure;
for i=1:15
    hold on;
    plot(data_gmId.NCH3_gm_Id(:,i),data_gmId.NCH3_Id_W(:,i),lineshape{i},'LineWidth',1.5);
    LL{i}=['Length=',num2str(L(i)),'um'];
end
xlabel('gm/Id,unit:S/A');
ylabel('Id/W,unit:A/m');
title('NCH3:Id/W - gm/Id');
legend(LL,'Location','Best');
grid on;

    case 2
%gm/gds - gm/Id
figure;
for i=1:15
    hold on;
    plot(data_gmId.NCH3_gm_Id(:,i),data_gmId.NCH3_gm_gds(:,i),lineshape{i},'LineWidth',1.5);
    LL{i}=['Length=',num2str(L(i)),'um'];
end
xlabel('gm/Id,unit:S/A');
ylabel('gm/gds');
title('NCH3:gm/gds - gm/Id');
legend(LL,'Location','Best');
grid on;

    case 3
%ft - gm/Id
figure;
for i=1:15
    hold on;
    plot(data_gmId.NCH3_gm_Id(:,i),data_gmId.NCH3_ft(:,i)/10^9,lineshape{i},'LineWidth',1.5);
    LL{i}=['Length=',num2str(L(i)),'um'];
end
xlabel('gm/Id,unit:S/A');
ylabel('ft,unit:GHz');
title('NCH3:ft - gm/Id');
legend(LL,'Location','Best');
grid on;

    case 4
%Vdsat - gm/Id
figure;
for i=1:15
    hold on;
    plot(data_gmId.NCH3_gm_Id(:,i),data_gmId.NCH3_Vdsat(:,i),lineshape{i},'LineWidth',1.5);
    LL{i}=['Length=',num2str(L(i)),'um'];
end
xlabel('gm/Id,unit:S/A');
ylabel('Vdsat,unit:V');
title('NCH3:Vdsat - gm/Id');
legend(LL,'Location','Best');
grid on;

    case 5
%Cgd/Cgg - gm/Id
figure;
for i=1:15
    hold on;
    plot(data_gmId.NCH3_gm_Id(:,i),data_gmId.NCH3_Cgd_Cgg(:,i),lineshape{i},'LineWidth',1.5);
    LL{i}=['Length=',num2str(L(i)),'um'];
end
xlabel('gm/Id,unit:S/A');
ylabel('Cgd/Cgg');
title('NCH3:Cgd/Cgg - gm/Id');
legend(LL,'Location','Best');
grid on;

    case 6
%Cdd/Cgg - gm/Id
figure;
for i=1:15
    hold on;
    plot(data_gmId.NCH3_gm_Id(:,i),data_gmId.NCH3_Cdd_Cgg(:,i),lineshape{i},'LineWidth',1.5);
    LL{i}=['Length=',num2str(L(i)),'um'];
end
xlabel('gm/Id,unit:S/A');
ylabel('Cdd/Cgg');
title('NCH3:Cdd/Cgg - gm/Id');
legend(LL,'Location','Best');
grid on;

    case 7
%Id/W - Vdsat
figure;
for i=1:15
    hold on;
    plot(data_gmId.NCH3_Vdsat(:,i),data_gmId.NCH3_Id_W(:,i),lineshape{i},'LineWidth',1.5);
    LL{i}=['Length=',num2str(L(i)),'um'];
end
xlabel('Vdsat,unit:V');
ylabel('Id/W,unit:A/m');
title('NCH3:Id/W - Vdsat');
legend(LL,'Location','Best');
grid on;

    case 8
%gm/Id - Vgs-Vth
figure;
for i=1:15
    hold on;
    plot(data_gmId.NCH3_Vgs_Vth(:,i),data_gmId.NCH3_gm_Id(:,i),lineshape{i},'LineWidth',1.5);
    LL{i}=['Length=',num2str(L(i)),'um'];
end
xlabel('Vgs-Vth,unit:V');
ylabel('gm/Id,unit:S/A');
title('NCH3:gm/Id - Vgs-Vth');
legend(LL,'Location','Best');
grid on;

    case 9
%Id/W - gm/Id
figure;
for i=1:15
    hold on;
    plot(data_gmId.PCH3_gm_Id(:,i),data_gmId.PCH3_Id_W(:,i),lineshape{i},'LineWidth',1.5);
    LL{i}=['Length=',num2str(L(i)),'um'];
end
xlabel('gm/Id,unit:S/A');
ylabel('Id/W,unit:A/m');
title('PCH3:Id/W - gm/Id');
legend(LL,'Location','Best');
grid on;

    case 10
%gm/gds - gm/Id
figure;
for i=1:15
    hold on;
    plot(data_gmId.PCH3_gm_Id(:,i),data_gmId.PCH3_gm_gds(:,i),lineshape{i},'LineWidth',1.5);
    LL{i}=['Length=',num2str(L(i)),'um'];
end
xlabel('gm/Id,unit:S/A');
ylabel('gm/gds');
title('PCH3:gm/gds - gm/Id');
legend(LL,'Location','Best');
grid on;

    case 11
%ft - gm/Id
figure;
for i=1:15
    hold on;
    plot(data_gmId.PCH3_gm_Id(:,i),data_gmId.PCH3_ft(:,i)/10^9,lineshape{i},'LineWidth',1.5);
    LL{i}=['Length=',num2str(L(i)),'um'];
end
xlabel('gm/Id,unit:S/A');
ylabel('ft,unit:GHz');
title('PCH3:ft - gm/Id');
legend(LL,'Location','Best');
grid on;

    case 12
%Vdsat - gm/Id
figure;
for i=1:15
    hold on;
    plot(data_gmId.PCH3_gm_Id(:,i),data_gmId.PCH3_Vdsat(:,i),lineshape{i},'LineWidth',1.5);
    LL{i}=['Length=',num2str(L(i)),'um'];
end
xlabel('gm/Id,unit:S/A');
ylabel('Vdsat,unit:V');
title('PCH3:Vdsat - gm/Id');
legend(LL,'Location','Best');
grid on;

    case 13
%Cgd/Cgg - gm/Id
figure;
for i=1:15
    hold on;
    plot(data_gmId.PCH3_gm_Id(:,i),data_gmId.PCH3_Cgd_Cgg(:,i),lineshape{i},'LineWidth',1.5);
    LL{i}=['Length=',num2str(L(i)),'um'];
end
xlabel('gm/Id,unit:S/A');
ylabel('Cgd/Cgg');
title('PCH3:Cgd/Cgg - gm/Id');
legend(LL,'Location','Best');
grid on;

    case 14
%Cdd/Cgg - gm/Id
figure;
for i=1:15
    hold on;
    plot(data_gmId.PCH3_gm_Id(:,i),data_gmId.PCH3_Cdd_Cgg(:,i),lineshape{i},'LineWidth',1.5);
    LL{i}=['Length=',num2str(L(i)),'um'];
end
xlabel('gm/Id,unit:S/A');
ylabel('Cdd/Cgg');
title('PCH3:Cdd/Cgg - gm/Id');
legend(LL,'Location','Best');
grid on;

    case 15
%Id/W - Vdsat
figure;
for i=1:15
    hold on;
    plot(data_gmId.PCH3_Vdsat(:,i),data_gmId.PCH3_Id_W(:,i),lineshape{i},'LineWidth',1.5);
    LL{i}=['Length=',num2str(L(i)),'um'];
end
xlabel('Vdsat,unit:V');
ylabel('Id/W,unit:A/m');
title('PCH3:Id/W - Vdsat');
legend(LL,'Location','Best');
grid on;

    case 16
%gm/Id - Vgs-Vth
figure;
for i=1:15
    hold on;
    plot(data_gmId.PCH3_Vgs_Vth(:,i),data_gmId.PCH3_gm_Id(:,i),lineshape{i},'LineWidth',1.5);
    LL{i}=['Length=',num2str(L(i)),'um'];
end
xlabel('Vgs-Vth,unit:V');
ylabel('gm/Id,unit:S/A');
title('PCH3:gm/Id - Vgs-Vth');
legend(LL,'Location','Best');
grid on;
end


% --- Executes on button press in pushbutton_Vds_draw.
function pushbutton_Vds_draw_Callback(hObject, eventdata, handles)
% hObject    handle to pushbutton_Vds_draw (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)

ll=get(handles.popupmenu_ll,'Value');
ll_num=[0.18, 0.2:0.1:1, 1.2:0.2:2.4];
global data_gmId;

%Vds_NCH3 plot
figure;
subplot(1,2,1), plot(data_gmId.Vds_NCH3_gm_Id(:,(ll-1)*10+1:10*ll),data_gmId.Vds_NCH3_gm_gds(:,(ll-1)*10+1:10*ll),'LineWidth',1.5);
grid on;
xlabel('gm/Id, unit:S/A');
ylabel('gm/gds');
title(['NCH3: gm/Id - gm/gds, Length=',num2str(ll_num(ll)),'um']);
legend('Vds=0.2V','Vds=0.25V','Vds=0.3V','Vds=0.35V','Vds=0.4V','Vds=0.45V','Vds=0.5V','Vds=0.55V','Vds=0.6V','Vds=0.65V');


%Vds_NCH3 plot
subplot(1,2,2), plot(data_gmId.Vds_PCH3_gm_Id(:,(ll-1)*10+1:10*ll),data_gmId.Vds_PCH3_gm_gds(:,(ll-1)*10+1:10*ll),'LineWidth',1.5);
grid on;
xlabel('gm/Id, unit:S/A');
ylabel('gm/gds');
title(['PCH3: gm/Id - gm/gds, Length=',num2str(ll_num(ll)),'um']);
legend('Vds=0.65V','Vds=0.6V','Vds=0.55V','Vds=0.5V','Vds=0.45V','Vds=0.4V','Vds=0.35V','Vds=0.3V','Vds=0.25V','Vds=0.2V');



function edit_nch3_para_gmId_Callback(hObject, eventdata, handles)
% hObject    handle to edit_nch3_para_gmId (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)

% Hints: get(hObject,'String') returns contents of edit_nch3_para_gmId as text
%        str2double(get(hObject,'String')) returns contents of edit_nch3_para_gmId as a double


% --- Executes during object creation, after setting all properties.
function edit_nch3_para_gmId_CreateFcn(hObject, eventdata, handles)
% hObject    handle to edit_nch3_para_gmId (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    empty - handles not created until after all CreateFcns called

% Hint: edit controls usually have a white background on Windows.
%       See ISPC and COMPUTER.
if ispc && isequal(get(hObject,'BackgroundColor'), get(0,'defaultUicontrolBackgroundColor'))
    set(hObject,'BackgroundColor','white');
end



function edit_nch3_para_Id_Callback(hObject, eventdata, handles)
% hObject    handle to edit_nch3_para_Id (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)

% Hints: get(hObject,'String') returns contents of edit_nch3_para_Id as text
%        str2double(get(hObject,'String')) returns contents of edit_nch3_para_Id as a double


% --- Executes during object creation, after setting all properties.
function edit_nch3_para_Id_CreateFcn(hObject, eventdata, handles)
% hObject    handle to edit_nch3_para_Id (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    empty - handles not created until after all CreateFcns called

% Hint: edit controls usually have a white background on Windows.
%       See ISPC and COMPUTER.
if ispc && isequal(get(hObject,'BackgroundColor'), get(0,'defaultUicontrolBackgroundColor'))
    set(hObject,'BackgroundColor','white');
end


% --- Executes on button press in pushbutton_nch3_para.
function pushbutton_nch3_para_Callback(hObject, eventdata, handles)
% hObject    handle to pushbutton_nch3_para (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)

ll=get(handles.popupmenu_ll,'Value');
ll_num=[0.18 0.2:0.1:1 1.2:0.2:2.4];
gm_Id=str2double(get(handles.edit_nch3_para_gmId,'String'));
Id=str2double(get(handles.edit_nch3_para_Id,'String'));

global data_gmId;
gm_Id_max=max(data_gmId.NCH3_gm_Id(:,ll));
gm_Id_min=min(data_gmId.NCH3_gm_Id(:,ll));

if gm_Id>=gm_Id_min && gm_Id<=gm_Id_max
%1.����Id/W
x=data_gmId.NCH3_gm_Id(:,ll);
y=data_gmId.NCH3_Id_W(:,ll);
Id_W=interp1(x,y,gm_Id);
%2.����Vdsat
x=data_gmId.NCH3_gm_Id(:,ll);
y=data_gmId.NCH3_Vdsat(:,ll);
Vdsat=interp1(x,y,gm_Id);
%3.����Vgs-Vth
x=data_gmId.NCH3_gm_Id(:,ll);
y=data_gmId.NCH3_Vgs_Vth(:,ll);
Vgs_Vth=interp1(x,y,gm_Id);
%4.����ft
x=data_gmId.NCH3_gm_Id(:,ll);
y=data_gmId.NCH3_ft(:,ll);
y=y/10^9;
ft=interp1(x,y,gm_Id);
%5.����gm/gds
x=data_gmId.NCH3_gm_Id(:,ll);
y=data_gmId.NCH3_gm_gds(:,ll);
gm_gds=interp1(x,y,gm_Id);
%6.����Cdd/Cgg
x=data_gmId.NCH3_gm_Id(:,ll);
y=data_gmId.NCH3_Cdd_Cgg(:,ll);
Cdd_Cgg=interp1(x,y,gm_Id);
%7.����Cgd/Cgg
x=data_gmId.NCH3_gm_Id(:,ll);
y=data_gmId.NCH3_Cgd_Cgg(:,ll);
Cgd_Cgg=interp1(x,y,gm_Id);

%�������в���
gm=gm_Id*Id;%uS
W=Id/Id_W;%um
Cgg=gm/2/pi/ft;%fF
gds=gm/gm_gds;%uS
Cdd=Cgg*Cdd_Cgg;%fF
Cgd=Cgg*Cgd_Cgg;%fF

outstr=['gm=',num2str(gm),'uS',10,'Vdsat=',num2str(Vdsat),'V',10,'W/L=',num2str(W),' / ',num2str(ll_num(ll)),'um',10,'gds=',num2str(gds),'uS',10,'Cgg=',num2str(Cgg),'fF',10,'Cdd=',num2str(Cdd),'fF',10,'Cgd=',num2str(Cgd),'fF'];
set(handles.edit_nch3_para,'String',outstr);
else
   set(handles.edit_nch3_para,'String','The input gm/Id is out of range!'); 
end


function edit_nch3_para_Callback(hObject, eventdata, handles)
% hObject    handle to edit_nch3_para (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)

% Hints: get(hObject,'String') returns contents of edit_nch3_para as text
%        str2double(get(hObject,'String')) returns contents of edit_nch3_para as a double


% --- Executes during object creation, after setting all properties.
function edit_nch3_para_CreateFcn(hObject, eventdata, handles)
% hObject    handle to edit_nch3_para (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    empty - handles not created until after all CreateFcns called

% Hint: edit controls usually have a white background on Windows.
%       See ISPC and COMPUTER.
if ispc && isequal(get(hObject,'BackgroundColor'), get(0,'defaultUicontrolBackgroundColor'))
    set(hObject,'BackgroundColor','white');
end



function edit_pch3_para_gmId_Callback(hObject, eventdata, handles)
% hObject    handle to edit_pch3_para_gmId (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)

% Hints: get(hObject,'String') returns contents of edit_pch3_para_gmId as text
%        str2double(get(hObject,'String')) returns contents of edit_pch3_para_gmId as a double


% --- Executes during object creation, after setting all properties.
function edit_pch3_para_gmId_CreateFcn(hObject, eventdata, handles)
% hObject    handle to edit_pch3_para_gmId (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    empty - handles not created until after all CreateFcns called

% Hint: edit controls usually have a white background on Windows.
%       See ISPC and COMPUTER.
if ispc && isequal(get(hObject,'BackgroundColor'), get(0,'defaultUicontrolBackgroundColor'))
    set(hObject,'BackgroundColor','white');
end



function edit_pch3_para_Id_Callback(hObject, eventdata, handles)
% hObject    handle to edit_pch3_para_Id (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)

% Hints: get(hObject,'String') returns contents of edit_pch3_para_Id as text
%        str2double(get(hObject,'String')) returns contents of edit_pch3_para_Id as a double


% --- Executes during object creation, after setting all properties.
function edit_pch3_para_Id_CreateFcn(hObject, eventdata, handles)
% hObject    handle to edit_pch3_para_Id (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    empty - handles not created until after all CreateFcns called

% Hint: edit controls usually have a white background on Windows.
%       See ISPC and COMPUTER.
if ispc && isequal(get(hObject,'BackgroundColor'), get(0,'defaultUicontrolBackgroundColor'))
    set(hObject,'BackgroundColor','white');
end


% --- Executes on button press in pushbutton_pch3_para.
function pushbutton_pch3_para_Callback(hObject, eventdata, handles)
% hObject    handle to pushbutton_pch3_para (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)

ll=get(handles.popupmenu_ll,'Value');
ll_num=[0.18 0.2:0.1:1 1.2:0.2:2.4];
gm_Id=str2double(get(handles.edit_pch3_para_gmId,'String'));
Id=str2double(get(handles.edit_pch3_para_Id,'String'));

global data_gmId;
gm_Id_max=max(data_gmId.PCH3_gm_Id(:,ll));
gm_Id_min=min(data_gmId.PCH3_gm_Id(:,ll));

if gm_Id>=gm_Id_min && gm_Id<=gm_Id_max
%1.����Id/W
x=data_gmId.PCH3_gm_Id(:,ll);
y=data_gmId.PCH3_Id_W(:,ll);
Id_W=interp1(x,y,gm_Id);
%2.����Vdsat
x=data_gmId.PCH3_gm_Id(:,ll);
y=data_gmId.PCH3_Vdsat(:,ll);
Vdsat=interp1(x,y,gm_Id);
%3.����Vgs-Vth
x=data_gmId.PCH3_gm_Id(:,ll);
y=data_gmId.PCH3_Vgs_Vth(:,ll);
Vgs_Vth=interp1(x,y,gm_Id);
%4.����ft
x=data_gmId.PCH3_gm_Id(:,ll);
y=data_gmId.PCH3_ft(:,ll);
y=y/10^9;
ft=interp1(x,y,gm_Id);
%5.����gm/gds
x=data_gmId.PCH3_gm_Id(:,ll);
y=data_gmId.PCH3_gm_gds(:,ll);
gm_gds=interp1(x,y,gm_Id);
%6.����Cdd/Cgg
x=data_gmId.PCH3_gm_Id(:,ll);
y=data_gmId.PCH3_Cdd_Cgg(:,ll);
Cdd_Cgg=interp1(x,y,gm_Id);
%7.����Cgd/Cgg
x=data_gmId.PCH3_gm_Id(:,ll);
y=data_gmId.PCH3_Cgd_Cgg(:,ll);
Cgd_Cgg=interp1(x,y,gm_Id);

%�������в���
gm=gm_Id*Id;%uS
W=Id/Id_W;%um
Cgg=gm/2/pi/ft;%fF
gds=gm/gm_gds;%uS
Cdd=Cgg*Cdd_Cgg;%fF
Cgd=Cgg*Cgd_Cgg;%fF

outstr=['gm=',num2str(gm),'uS',10,'Vdsat=',num2str(Vdsat),'V',10,'W/L=',num2str(W),' / ',num2str(ll_num(ll)),'um',10,'gds=',num2str(gds),'uS',10,'Cgg=',num2str(Cgg),'fF',10,'Cdd=',num2str(Cdd),'fF',10,'Cgd=',num2str(Cgd),'fF'];
set(handles.edit_pch3_para,'String',outstr);
else
   set(handles.edit_pch3_para,'String','The input gm/Id is out of range!'); 
end


function edit_pch3_para_Callback(hObject, eventdata, handles)
% hObject    handle to edit_pch3_para (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)

% Hints: get(hObject,'String') returns contents of edit_pch3_para as text
%        str2double(get(hObject,'String')) returns contents of edit_pch3_para as a double


% --- Executes during object creation, after setting all properties.
function edit_pch3_para_CreateFcn(hObject, eventdata, handles)
% hObject    handle to edit_pch3_para (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    empty - handles not created until after all CreateFcns called

% Hint: edit controls usually have a white background on Windows.
%       See ISPC and COMPUTER.
if ispc && isequal(get(hObject,'BackgroundColor'), get(0,'defaultUicontrolBackgroundColor'))
    set(hObject,'BackgroundColor','white');
end
