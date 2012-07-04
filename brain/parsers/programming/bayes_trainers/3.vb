Imports ADOX
Imports System.Data.OleDb

Module ExportLab
    Public Function ExportLab(ByVal ImportTabIndex As Integer, ByVal DatabasePath As String)

        If FileIO.FileSystem.FileExists(DatabasePath) = True Then
            'ControlGUI.ds(ControlGUI.TabControl1.SelectedIndex - 7).Dispose()
            FileIO.FileSystem.DeleteFile(DatabasePath)
        End If

        If FileIO.FileSystem.FileExists(DatabasePath) = False Then CreateAccessDatabase(DatabasePath)

        Dim cn As New OleDb.OleDbConnection
        Dim da As New OleDb.OleDbDataAdapter
        Dim sql As String

        Dim dbProvider As String = "Provider=Microsoft.Jet.OLEDB.4.0;"
        Dim dbSource As String = "Data Source = " & DatabasePath
        cn.ConnectionString = dbProvider & dbSource
        'ControlGUI.TabPropertiesGrid.DataBindings.DefaultDataSourceUpdateMode = DataSourceUpdateMode.OnValidation

        'ControlGUI.da(ImportTabIndex).Update(ControlGUI.ds(ImportTabIndex).Tables.Item("Tab"))
        'ControlGUI.ds(ImportTabIndex).AcceptChanges()

        sql = "INSERT INTO Tab VALUES ('0', '" & ControlGUI.ds(ControlGUI.TabControl1.SelectedIndex - 7).Tables("Tab").Rows.Item(0).Item(1).ToString & "', '" & ControlGUI.ds(ControlGUI.TabControl1.SelectedIndex - 7).Tables("Tab").Rows.Item(0).Item(2).ToString & "')"
        da = New OleDb.OleDbDataAdapter(sql, cn)
        da.Fill(ControlGUI.ds(ControlGUI.TabControl1.SelectedIndex - 7), "Tab")

        Dim rownum As Integer = 0
        Do While rownum < ControlGUI.ds(ControlGUI.TabControl1.SelectedIndex - 7).Tables("Button").Rows.Count
            sql = "INSERT INTO Button VALUES (" & rownum & ", '" & _
                 ControlGUI.ds(ControlGUI.TabControl1.SelectedIndex - 7).Tables("Button").Rows.Item(rownum).Item(1).ToString & "'" & _
                ", " & ControlGUI.ds(ControlGUI.TabControl1.SelectedIndex - 7).Tables("Button").Rows.Item(rownum).Item(2).ToString & _
                ", " & ControlGUI.ds(ControlGUI.TabControl1.SelectedIndex - 7).Tables("Button").Rows.Item(rownum).Item(3).ToString & _
                ", " & ControlGUI.ds(ControlGUI.TabControl1.SelectedIndex - 7).Tables("Button").Rows.Item(rownum).Item(4).ToString & _
                ", " & ControlGUI.ds(ControlGUI.TabControl1.SelectedIndex - 7).Tables("Button").Rows.Item(rownum).Item(5).ToString & _
                ", " & ControlGUI.ds(ControlGUI.TabControl1.SelectedIndex - 7).Tables("Button").Rows.Item(rownum).Item(6).ToString & ")"

            da = New OleDb.OleDbDataAdapter(sql, cn)
            da.Fill(ControlGUI.ds(ControlGUI.TabControl1.SelectedIndex - 7), "Button")
            rownum = rownum + 1
        Loop

        rownum = 0
        Do While rownum < ControlGUI.ds(ControlGUI.TabControl1.SelectedIndex - 7).Tables("Label").Rows.Count
            sql = "INSERT INTO Label VALUES (" & rownum & ", '" & _
                 ControlGUI.ds(ControlGUI.TabControl1.SelectedIndex - 7).Tables("Label").Rows.Item(rownum).Item(1).ToString & "'" & _
                ", " & ControlGUI.ds(ControlGUI.TabControl1.SelectedIndex - 7).Tables("Label").Rows.Item(rownum).Item(2).ToString & _
                ", " & ControlGUI.ds(ControlGUI.TabControl1.SelectedIndex - 7).Tables("Label").Rows.Item(rownum).Item(3).ToString & ")"

            da = New OleDb.OleDbDataAdapter(sql, cn)
            da.Fill(ControlGUI.ds(ControlGUI.TabControl1.SelectedIndex - 7), "Label")
            rownum = rownum + 1
        Loop

        rownum = 0
        Do While rownum < ControlGUI.ds(ControlGUI.TabControl1.SelectedIndex - 7).Tables("StatusLabel").Rows.Count
            sql = "INSERT INTO StatusLabel VALUES (" & rownum & ", '" & _
                 ControlGUI.ds(ControlGUI.TabControl1.SelectedIndex - 7).Tables("StatusLabel").Rows.Item(rownum).Item(1).ToString & "'" & _
                  ", '" & ControlGUI.ds(ControlGUI.TabControl1.SelectedIndex - 7).Tables("StatusLabel").Rows.Item(rownum).Item(2).ToString & "'" & _
                ", '" & ControlGUI.ds(ControlGUI.TabControl1.SelectedIndex - 7).Tables("StatusLabel").Rows.Item(rownum).Item(3).ToString & "'" & _
                ", " & ControlGUI.ds(ControlGUI.TabControl1.SelectedIndex - 7).Tables("StatusLabel").Rows.Item(rownum).Item(4).ToString & _
                ", " & ControlGUI.ds(ControlGUI.TabControl1.SelectedIndex - 7).Tables("StatusLabel").Rows.Item(rownum).Item(5).ToString & _
                ", " & ControlGUI.ds(ControlGUI.TabControl1.SelectedIndex - 7).Tables("StatusLabel").Rows.Item(rownum).Item(6).ToString & _
                ", " & ControlGUI.ds(ControlGUI.TabControl1.SelectedIndex - 7).Tables("StatusLabel").Rows.Item(rownum).Item(7).ToString & _
                ", '" & ControlGUI.ds(ControlGUI.TabControl1.SelectedIndex - 7).Tables("StatusLabel").Rows.Item(rownum).Item(8).ToString & "'" & _
                ", " & ControlGUI.ds(ControlGUI.TabControl1.SelectedIndex - 7).Tables("StatusLabel").Rows.Item(rownum).Item(9).ToString & _
                ", " & ControlGUI.ds(ControlGUI.TabControl1.SelectedIndex - 7).Tables("StatusLabel").Rows.Item(rownum).Item(10).ToString & ")"

            da = New OleDb.OleDbDataAdapter(sql, cn)
            da.Fill(ControlGUI.ds(ControlGUI.TabControl1.SelectedIndex - 7), "StatusLabel")
            rownum = rownum + 1
        Loop

        rownum = 0
        Do While rownum < ControlGUI.ds(ControlGUI.TabControl1.SelectedIndex - 7).Tables("Picture").Rows.Count

            sql = "INSERT INTO Picture VALUES (" & rownum & ", '" & _
                 ControlGUI.ds(ControlGUI.TabControl1.SelectedIndex - 7).Tables("Picture").Rows.Item(rownum).Item(1).ToString & "'" & _
                 ", '" & ControlGUI.ds(ControlGUI.TabControl1.SelectedIndex - 7).Tables("Picture").Rows.Item(rownum).Item(2).ToString & "'" & _
                ", " & ControlGUI.ds(ControlGUI.TabControl1.SelectedIndex - 7).Tables("Picture").Rows.Item(rownum).Item(3).ToString & _
                ", " & ControlGUI.ds(ControlGUI.TabControl1.SelectedIndex - 7).Tables("Picture").Rows.Item(rownum).Item(4).ToString & _
                ", " & ControlGUI.ds(ControlGUI.TabControl1.SelectedIndex - 7).Tables("Picture").Rows.Item(rownum).Item(5).ToString & _
                ", " & ControlGUI.ds(ControlGUI.TabControl1.SelectedIndex - 7).Tables("Picture").Rows.Item(rownum).Item(6).ToString & ")"

            da = New OleDb.OleDbDataAdapter(sql, cn)
            da.Fill(ControlGUI.ds(ControlGUI.TabControl1.SelectedIndex - 7), "Picture")
            rownum = rownum + 1
        Loop

        rownum = 0
        Do While rownum < ControlGUI.ds(ControlGUI.TabControl1.SelectedIndex - 7).Tables("Gauge").Rows.Count
            sql = "INSERT INTO Gauge VALUES (" & rownum & ", '" & _
                 ControlGUI.ds(ControlGUI.TabControl1.SelectedIndex - 7).Tables("Gauge").Rows.Item(rownum).Item(1).ToString & "'" & _
                ", " & ControlGUI.ds(ControlGUI.TabControl1.SelectedIndex - 7).Tables("Gauge").Rows.Item(rownum).Item(2).ToString & _
                ", " & ControlGUI.ds(ControlGUI.TabControl1.SelectedIndex - 7).Tables("Gauge").Rows.Item(rownum).Item(3).ToString & _
                ", " & ControlGUI.ds(ControlGUI.TabControl1.SelectedIndex - 7).Tables("Gauge").Rows.Item(rownum).Item(4).ToString & _
                ", " & ControlGUI.ds(ControlGUI.TabControl1.SelectedIndex - 7).Tables("Gauge").Rows.Item(rownum).Item(5).ToString & _
                ", '" & ControlGUI.ds(ControlGUI.TabControl1.SelectedIndex - 7).Tables("Gauge").Rows.Item(rownum).Item(6).ToString & "'" & _
                ", " & ControlGUI.ds(ControlGUI.TabControl1.SelectedIndex - 7).Tables("Gauge").Rows.Item(rownum).Item(7).ToString & _
                ", " & ControlGUI.ds(ControlGUI.TabControl1.SelectedIndex - 7).Tables("Gauge").Rows.Item(rownum).Item(8).ToString & _
                ", " & ControlGUI.ds(ControlGUI.TabControl1.SelectedIndex - 7).Tables("Gauge").Rows.Item(rownum).Item(9).ToString & _
                ", " & ControlGUI.ds(ControlGUI.TabControl1.SelectedIndex - 7).Tables("Gauge").Rows.Item(rownum).Item(10).ToString & _
                ", '" & ControlGUI.ds(ControlGUI.TabControl1.SelectedIndex - 7).Tables("Gauge").Rows.Item(rownum).Item(11).ToString & "')"


            da = New OleDb.OleDbDataAdapter(sql, cn)
            da.Fill(ControlGUI.ds(ControlGUI.TabControl1.SelectedIndex - 7), "Gauge")
            rownum = rownum + 1
        Loop

        ControlGUI.LabPageListBox.Items.Remove(ControlGUI.LabPageListBox.Items.Item(ControlGUI.TabPageIndexToImportTabCount(ControlGUI.TabControl1.SelectedIndex)))
        ControlGUI.TabPropertiesGrid.DataSource = Nothing
        ControlGUI.TabPropertiesGrid.DataMember = Nothing
        ControlGUI.TabPropertiesTableText.Text = ""
        ControlGUI.TabPropertiesTableText.Tag = -1
        ControlGUI.TabControl1.SelectedTab.Dispose()
        ControlGUI.ImportTabCount = ControlGUI.ImportTabCount - 1
        'ControlGUI.TabControl1.SelectedTab.Dispose()

        ImportLab.ImportLab(DatabasePath)



    End Function

    Private Function CreateAccessDatabase(ByVal DatabaseFullPath As String) As Boolean
        Dim cat As ADOX.Catalog = New ADOX.Catalog()
        Dim bAns As Boolean = False

        'Try
        cat.Create("Provider=Microsoft.Jet.OLEDB.4.0;Data Source=" & DatabaseFullPath & ";Jet OLEDB:Engine Type=5")

        'Create Tab Table
        Dim Table_Tab As New ADOX.Table
        Table_Tab.Name = "Tab"
        cat.Tables.Append(Table_Tab)


        Dim Tab_ID As New ADOX.Column
        Tab_ID.Name = "ID"
        cat.Tables("Tab").Columns.Append(Tab_ID)

        Dim Tab_BackgroundImagePathCol As New ADOX.Column
        Tab_BackgroundImagePathCol.Name = "BackgroundImagePathCol"
        cat.Tables("Tab").Columns.Append(Tab_BackgroundImagePathCol)

        Dim Tab_TextCol As New ADOX.Column
        Tab_TextCol.Name = "TextCol"
        cat.Tables("Tab").Columns.Append(Tab_TextCol)

        'Create Button Table
        Dim Table_Button As New ADOX.Table
        Table_Button.Name = "Button"
        cat.Tables.Append(Table_Button)


        Dim Button_ID As New ADOX.Column
        Button_ID.Name = "ID"
        cat.Tables("Button").Columns.Append(Button_ID)

        Dim Button_NameCol As New ADOX.Column
        Button_NameCol.Name = "NameCol"
        cat.Tables("Button").Columns.Append(Button_NameCol)

        Dim Button_XCol As New ADOX.Column
        Button_XCol.Name = "XCol"
        cat.Tables("Button").Columns.Append(Button_XCol)

        Dim Button_YCol As New ADOX.Column
        Button_YCol.Name = "YCol"
        cat.Tables("Button").Columns.Append(Button_YCol)

        Dim Button_WidthCol As New ADOX.Column
        Button_WidthCol.Name = "WidthCol"
        cat.Tables("Button").Columns.Append(Button_WidthCol)

        Dim Button_HeightCol As New ADOX.Column
        Button_HeightCol.Name = "HeightCol"
        cat.Tables("Button").Columns.Append(Button_HeightCol)

        Dim Button_PinCol As New ADOX.Column
        Button_PinCol.Name = "PinCol"
        cat.Tables("Button").Columns.Append(Button_PinCol)

        'Create Label Table
        Dim Table_Label As New ADOX.Table
        Table_Label.Name = "Label"
        cat.Tables.Append(Table_Label)


        Dim Label_ID As New ADOX.Column
        Label_ID.Name = "ID"
        cat.Tables("Label").Columns.Append(Label_ID)

        Dim Label_TextCol As New ADOX.Column
        Label_TextCol.Name = "TextCol"
        cat.Tables("Label").Columns.Append(Label_TextCol)

        Dim Label_XCol As New ADOX.Column
        Label_XCol.Name = "XCol"
        cat.Tables("Label").Columns.Append(Label_XCol)

        Dim Label_YCol As New ADOX.Column
        Label_YCol.Name = "YCol"
        cat.Tables("Label").Columns.Append(Label_YCol)

        'Create StatusLabel Table
        Dim Table_StatusLabel As New ADOX.Table
        Table_StatusLabel.Name = "StatusLabel"
        cat.Tables.Append(Table_StatusLabel)


        Dim StatusLabel_ID As New ADOX.Column
        StatusLabel_ID.Name = "ID"
        cat.Tables("StatusLabel").Columns.Append(StatusLabel_ID)

        Dim StatusLabel_LowerTextCol As New ADOX.Column
        StatusLabel_LowerTextCol.Name = "LowerTextCol"
        cat.Tables("StatusLabel").Columns.Append(StatusLabel_LowerTextCol)

        Dim StatusLabel_NormalTextCol As New ADOX.Column
        StatusLabel_NormalTextCol.Name = "NormalTextCol"
        cat.Tables("StatusLabel").Columns.Append(StatusLabel_NormalTextCol)

        Dim StatusLabel_HigherTextCol As New ADOX.Column
        StatusLabel_HigherTextCol.Name = "HigherTextCol"
        cat.Tables("StatusLabel").Columns.Append(StatusLabel_HigherTextCol)

        Dim StatusLabel_XCol As New ADOX.Column
        StatusLabel_XCol.Name = "XCol"
        cat.Tables("StatusLabel").Columns.Append(StatusLabel_XCol)

        Dim StatusLabel_YCol As New ADOX.Column
        StatusLabel_YCol.Name = "YCol"
        cat.Tables("StatusLabel").Columns.Append(StatusLabel_YCol)

        Dim StatusLabel_WidthCol As New ADOX.Column
        StatusLabel_WidthCol.Name = "WidthCol"
        cat.Tables("StatusLabel").Columns.Append(StatusLabel_WidthCol)

        Dim StatusLabel_HeightCol As New ADOX.Column
        StatusLabel_HeightCol.Name = "HeightCol"
        cat.Tables("StatusLabel").Columns.Append(StatusLabel_HeightCol)

        Dim StatusLabel_DeviceCol As New ADOX.Column
        StatusLabel_DeviceCol.Name = "DeviceCol"
        cat.Tables("StatusLabel").Columns.Append(StatusLabel_DeviceCol)

        Dim StatusLabel_MinValueCol As New ADOX.Column
        StatusLabel_MinValueCol.Name = "MinValueCol"
        cat.Tables("StatusLabel").Columns.Append(StatusLabel_MinValueCol)

        Dim StatusLabel_MaxValueCol As New ADOX.Column
        StatusLabel_MaxValueCol.Name = "MaxValueCol"
        cat.Tables("StatusLabel").Columns.Append(StatusLabel_MaxValueCol)


        'Create Picture Table
        Dim Table_Picture As New ADOX.Table
        Table_Picture.Name = "Picture"
        cat.Tables.Append(Table_Picture)


        Dim Picture_ID As New ADOX.Column
        Picture_ID.Name = "ID"
        cat.Tables("Picture").Columns.Append(Picture_ID)

        Dim Picture_NameCol As New ADOX.Column
        Picture_NameCol.Name = "NameCol"
        cat.Tables("Picture").Columns.Append(Picture_NameCol)

        Dim Picture_PicPathCol As New ADOX.Column
        Picture_PicPathCol.Name = "PicPathCol"
        cat.Tables("Picture").Columns.Append(Picture_PicPathCol)

        Dim Picture_XCol As New ADOX.Column
        Picture_XCol.Name = "XCol"
        cat.Tables("Picture").Columns.Append(Picture_XCol)

        Dim Picture_YCol As New ADOX.Column
        Picture_YCol.Name = "YCol"
        cat.Tables("Picture").Columns.Append(Picture_YCol)

        Dim Picture_WidthCol As New ADOX.Column
        Picture_WidthCol.Name = "WidthCol"
        cat.Tables("Picture").Columns.Append(Picture_WidthCol)

        Dim Picture_HeightCol As New ADOX.Column
        Picture_HeightCol.Name = "HeightCol"
        cat.Tables("Picture").Columns.Append(Picture_HeightCol)

        'Create Gauge Table
        Dim Table_Gauge As New ADOX.Table
        Table_Gauge.Name = "Gauge"
        cat.Tables.Append(Table_Gauge)


        Dim Gauge_ID As New ADOX.Column
        Gauge_ID.Name = "ID"
        cat.Tables("Gauge").Columns.Append(Gauge_ID)

        Dim Gauge_TextCol As New ADOX.Column
        Gauge_TextCol.Name = "TextCol"
        cat.Tables("Gauge").Columns.Append(Gauge_TextCol)

        Dim Gauge_XCol As New ADOX.Column
        Gauge_XCol.Name = "XCol"
        cat.Tables("Gauge").Columns.Append(Gauge_XCol)

        Dim Gauge_YCol As New ADOX.Column
        Gauge_YCol.Name = "YCol"
        cat.Tables("Gauge").Columns.Append(Gauge_YCol)

        Dim Gauge_WidthCol As New ADOX.Column
        Gauge_WidthCol.Name = "WidthCol"
        cat.Tables("Gauge").Columns.Append(Gauge_WidthCol)

        Dim Gauge_HeightCol As New ADOX.Column
        Gauge_HeightCol.Name = "HeightCol"
        cat.Tables("Gauge").Columns.Append(Gauge_HeightCol)

        Dim Gauge_DeviceCol As New ADOX.Column
        Gauge_DeviceCol.Name = "DeviceCol"
        cat.Tables("Gauge").Columns.Append(Gauge_DeviceCol)

        Dim Gauge_MinValueCol As New ADOX.Column
        Gauge_MinValueCol.Name = "MinValueCol"
        cat.Tables("Gauge").Columns.Append(Gauge_MinValueCol)

        Dim Gauge_MaxValueCol As New ADOX.Column
        Gauge_MaxValueCol.Name = "MaxValueCol"
        cat.Tables("Gauge").Columns.Append(Gauge_MaxValueCol)

        Dim Gauge_RecommendedValueCol As New ADOX.Column
        Gauge_RecommendedValueCol.Name = "RecommendedValueCol"
        cat.Tables("Gauge").Columns.Append(Gauge_RecommendedValueCol)

        Dim Gauge_ThresholdPercentCol As New ADOX.Column
        Gauge_ThresholdPercentCol.Name = "ThresholdPercentCol"
        cat.Tables("Gauge").Columns.Append(Gauge_ThresholdPercentCol)

        Dim Gauge_BackColorCol As New ADOX.Column
        Gauge_BackColorCol.Name = "BackColorCol"
        cat.Tables("Gauge").Columns.Append(Gauge_BackColorCol)

        MessageBox.Show("Database Created Successfully")
        bAns = True

        'Catch Excep As System.Runtime.InteropServices.COMException
        'MsgBox(Excep.ToString)
        'Finally
        cat = Nothing
        'End Try
        Return bAns
    End Function

End Module