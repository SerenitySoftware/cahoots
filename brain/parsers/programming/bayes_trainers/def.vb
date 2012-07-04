VERSION 1.0 CLASS
BEGIN
  MultiUse = -1  'True
  Persistable = 0  'NotPersistable
  DataBindingBehavior = 0  'vbNone
  DataSourceBehavior  = 0  'vbNone
  MTSTransactionMode  = 0  'NotAnMTSObject
END
Attribute VB_Name = "clsDocParserAdapter"
Attribute VB_GlobalNameSpace = False
Attribute VB_Creatable = True
Attribute VB_PredeclaredId = False
Attribute VB_Exposed = True
'*
'*      VBDOX - Visual Basic Documentation Generator
'*      Copyright (c) 2000 - 2003 Mihayl Stamenov <michael.stamenov@web.de>
'*
'* This program is free software; you can redistribute it and/or modify
'* it under the terms of the GNU General Public License as published by
'* the Free Software Foundation; either version 2, or (at your option)
'* any later version.
'*
'* This program is distributed in the hope that it will be useful,
'* but WITHOUT ANY WARRANTY; without even the implied warranty of
'* MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
'* GNU General Public License for more details.
'*
'* You should have received a copy of the GNU General Public License
'* along with this program; see the file COPYING.  If not, write to
'* the Free Software Foundation, 675 Mass Ave, Cambridge, MA 02139, USA.
'*

''
' Documentation comment parser adapter for ASP and VBScript
'
' @author m.stamenov
' @date 20020121

Option Explicit

Private dp   As IDocParser

Public Sub setDocParser(ByVal docParser As IDocParser)

    Set dp = docParser

End Sub

''
' Tells whether the module has documentation comment
'
' @param module Specifies the module checked for description
' @return True if the module has documentation description
Public Function hasModuleDescription(ByVal module As clsModule) As Boolean
    
    If Not (dp Is Nothing) Then
        hasModuleDescription = dp.hasModuleDescription(module)
    End If

End Function

''
' The description of the module
'
' @param module Specifies the module for which to
'               return a documentation description
' @return String description of the module
Public Function getModuleDescription(ByVal module As clsModule) As String
    
    If Not (dp Is Nothing) Then
        getModuleDescription = dp.getModuleDescription(module)
    End If

End Function

''
' The description of function, subroutine, enumeration,
' declaration or other module entry
'
' @param entry Specifies the entry for which to
'               return a documentation description
' @return String description of the entry
Public Function getDescription(ByVal entry As clsEntry) As String
    
    If Not (dp Is Nothing) Then
        getDescription = dp.getDescription(entry)
    End If

End Function

''
' The description of entry return value
'
' @param entry  Specifies the entry for which to
'               return a return value description
' @return String description of the entry return value
Public Function getReturnValue(ByVal entry As clsEntry) As String
    
    If Not (dp Is Nothing) Then
        getReturnValue = dp.getReturnValue(entry)
    End If

End Function

''
' The remarks about the entry
'
' @param entry  Specifies the entry for which to
'               return a remarks
' @return String remarks about the entry
Public Function getRemarks(ByVal entry As clsEntry) As String
    
    If Not (dp Is Nothing) Then
        getRemarks = dp.getRemarks(entry)
    End If

End Function

Public Function getParam(ByVal entry As clsEntry, ByVal param As clsParam) As String
    
    If Not (dp Is Nothing) Then
        getParam = dp.getParam(entry, param)
    End If

End Function

Public Function getEnumValue(ByVal entry As clsEntry, ByVal param As clsParam) As String
    
    If Not (dp Is Nothing) Then
        getEnumValue = dp.getEnumValue(entry, param)
    End If

End Function

''
' Returns module documentation property by name
' This is intended for extended documentation comment
' properties not accessible by the standart IDocParser methods
'
' @param module Specifies the module for which to return a property
' @param prop   Specifies the name of the property to get
' @param index  Specifies the index of the property in the collection
' @return The string value of the property
Public Function getModuleProperty(ByVal module As clsModule, ByVal prop As String, Optional ByVal index As Long = 1) As String
    
    If Not (dp Is Nothing) Then
        getModuleProperty = dp.getModuleProperty(module, prop, index)
    End If

End Function

''
' Returns entry documentation property by name
' This is intended for extended documentation comment
' properties not accessible by the standart IDocParser methods
'
' @param entry Specifies the entry for which to return a property
' @param prop   Specifies the name of the property to get
' @param index  Specifies the index of the property in the collection
' @return The string value of the property
Public Function getEntryProperty(ByVal entry As clsEntry, ByVal prop As String, Optional ByVal index As Long = 1) As String
    
    If Not (dp Is Nothing) Then
        getEntryProperty = dp.getEntryProperty(entry, prop, index)
    End If

End Function

' end of file

﻿'------------------------------------------------------------------------------
' <auto-generated>
'     This code was generated by a tool.
'     Runtime Version:4.0.30319.239
'
'     Changes to this file may cause incorrect behavior and will be lost if
'     the code is regenerated.
' </auto-generated>
'------------------------------------------------------------------------------

Option Strict Off
Option Explicit On



'''<summary>
'''Represents a strongly typed in-memory cache of data.
'''</summary>
<Global.System.Serializable(),  _
 Global.System.ComponentModel.DesignerCategoryAttribute("code"),  _
 Global.System.ComponentModel.ToolboxItem(true),  _
 Global.System.Xml.Serialization.XmlSchemaProviderAttribute("GetTypedDataSetSchema"),  _
 Global.System.Xml.Serialization.XmlRootAttribute("DatalogDataSet"),  _
 Global.System.ComponentModel.Design.HelpKeywordAttribute("vs.data.DataSet")>  _
Partial Public Class DatalogDataSet
    Inherits Global.System.Data.DataSet
    
    Private tableHumidity_Sensor As Humidity_SensorDataTable
    
    Private tablepH_Sensor As pH_SensorDataTable
    
    Private tableTemperature_Sensor As Temperature_SensorDataTable
    
    Private _schemaSerializationMode As Global.System.Data.SchemaSerializationMode = Global.System.Data.SchemaSerializationMode.IncludeSchema
    
    <Global.System.Diagnostics.DebuggerNonUserCodeAttribute(),  _
     Global.System.CodeDom.Compiler.GeneratedCodeAttribute("System.Data.Design.TypedDataSetGenerator", "4.0.0.0")>  _
    Public Sub New()
        MyBase.New
        Me.BeginInit
        Me.InitClass
        Dim schemaChangedHandler As Global.System.ComponentModel.CollectionChangeEventHandler = AddressOf Me.SchemaChanged
        AddHandler MyBase.Tables.CollectionChanged, schemaChangedHandler
        AddHandler MyBase.Relations.CollectionChanged, schemaChangedHandler
        Me.EndInit
    End Sub
    
    <Global.System.Diagnostics.DebuggerNonUserCodeAttribute(),  _
     Global.System.CodeDom.Compiler.GeneratedCodeAttribute("System.Data.Design.TypedDataSetGenerator", "4.0.0.0")>  _
    Protected Sub New(ByVal info As Global.System.Runtime.Serialization.SerializationInfo, ByVal context As Global.System.Runtime.Serialization.StreamingContext)
        MyBase.New(info, context, false)
        If (Me.IsBinarySerialized(info, context) = true) Then
            Me.InitVars(false)
            Dim schemaChangedHandler1 As Global.System.ComponentModel.CollectionChangeEventHandler = AddressOf Me.SchemaChanged
            AddHandler Me.Tables.CollectionChanged, schemaChangedHandler1
            AddHandler Me.Relations.CollectionChanged, schemaChangedHandler1
            Return
        End If
        Dim strSchema As String = CType(info.GetValue("XmlSchema", GetType(String)),String)
        If (Me.DetermineSchemaSerializationMode(info, context) = Global.System.Data.SchemaSerializationMode.IncludeSchema) Then
            Dim ds As Global.System.Data.DataSet = New Global.System.Data.DataSet()
            ds.ReadXmlSchema(New Global.System.Xml.XmlTextReader(New Global.System.IO.StringReader(strSchema)))
            If (Not (ds.Tables("Humidity Sensor")) Is Nothing) Then
                MyBase.Tables.Add(New Humidity_SensorDataTable(ds.Tables("Humidity Sensor")))
            End If
            If (Not (ds.Tables("pH Sensor")) Is Nothing) Then
                MyBase.Tables.Add(New pH_SensorDataTable(ds.Tables("pH Sensor")))
            End If
            If (Not (ds.Tables("Temperature Sensor")) Is Nothing) Then
                MyBase.Tables.Add(New Temperature_SensorDataTable(ds.Tables("Temperature Sensor")))
            End If
            Me.DataSetName = ds.DataSetName
            Me.Prefix = ds.Prefix
            Me.Namespace = ds.Namespace
            Me.Locale = ds.Locale
            Me.CaseSensitive = ds.CaseSensitive
            Me.EnforceConstraints = ds.EnforceConstraints
            Me.Merge(ds, false, Global.System.Data.MissingSchemaAction.Add)
            Me.InitVars
        Else
            Me.ReadXmlSchema(New Global.System.Xml.XmlTextReader(New Global.System.IO.StringReader(strSchema)))
        End If
        Me.GetSerializationData(info, context)
        Dim schemaChangedHandler As Global.System.ComponentModel.CollectionChangeEventHandler = AddressOf Me.SchemaChanged
        AddHandler MyBase.Tables.CollectionChanged, schemaChangedHandler
        AddHandler Me.Relations.CollectionChanged, schemaChangedHandler
    End Sub
    
    <Global.System.Diagnostics.DebuggerNonUserCodeAttribute(),  _
     Global.System.CodeDom.Compiler.GeneratedCodeAttribute("System.Data.Design.TypedDataSetGenerator", "4.0.0.0"),  _
     Global.System.ComponentModel.Browsable(false),  _
     Global.System.ComponentModel.DesignerSerializationVisibility(Global.System.ComponentModel.DesignerSerializationVisibility.Content)>  _
    Public ReadOnly Property Humidity_Sensor() As Humidity_SensorDataTable
        Get
            Return Me.tableHumidity_Sensor
        End Get
    End Property
    
    <Global.System.Diagnostics.DebuggerNonUserCodeAttribute(),  _
     Global.System.CodeDom.Compiler.GeneratedCodeAttribute("System.Data.Design.TypedDataSetGenerator", "4.0.0.0"),  _
     Global.System.ComponentModel.Browsable(false),  _
     Global.System.ComponentModel.DesignerSerializationVisibility(Global.System.ComponentModel.DesignerSerializationVisibility.Content)>  _
    Public ReadOnly Property pH_Sensor() As pH_SensorDataTable
        Get
            Return Me.tablepH_Sensor
        End Get
    End Property
    
    <Global.System.Diagnostics.DebuggerNonUserCodeAttribute(),  _
     Global.System.CodeDom.Compiler.GeneratedCodeAttribute("System.Data.Design.TypedDataSetGenerator", "4.0.0.0"),  _
     Global.System.ComponentModel.Browsable(false),  _
     Global.System.ComponentModel.DesignerSerializationVisibility(Global.System.ComponentModel.DesignerSerializationVisibility.Content)>  _
    Public ReadOnly Property Temperature_Sensor() As Temperature_SensorDataTable
        Get
            Return Me.tableTemperature_Sensor
        End Get
    End Property
    
    <Global.System.Diagnostics.DebuggerNonUserCodeAttribute(),  _
     Global.System.CodeDom.Compiler.GeneratedCodeAttribute("System.Data.Design.TypedDataSetGenerator", "4.0.0.0"),  _
     Global.System.ComponentModel.BrowsableAttribute(true),  _
     Global.System.ComponentModel.DesignerSerializationVisibilityAttribute(Global.System.ComponentModel.DesignerSerializationVisibility.Visible)>  _
    Public Overrides Property SchemaSerializationMode() As Global.System.Data.SchemaSerializationMode
        Get
            Return Me._schemaSerializationMode
        End Get
        Set
            Me._schemaSerializationMode = value
        End Set
    End Property
    
    <Global.System.Diagnostics.DebuggerNonUserCodeAttribute(),  _
     Global.System.CodeDom.Compiler.GeneratedCodeAttribute("System.Data.Design.TypedDataSetGenerator", "4.0.0.0"),  _
     Global.System.ComponentModel.DesignerSerializationVisibilityAttribute(Global.System.ComponentModel.DesignerSerializationVisibility.Hidden)>  _
    Public Shadows ReadOnly Property Tables() As Global.System.Data.DataTableCollection
        Get
            Return MyBase.Tables
        End Get
    End Property
    
    <Global.System.Diagnostics.DebuggerNonUserCodeAttribute(),  _
     Global.System.CodeDom.Compiler.GeneratedCodeAttribute("System.Data.Design.TypedDataSetGenerator", "4.0.0.0"),  _
     Global.System.ComponentModel.DesignerSerializationVisibilityAttribute(Global.System.ComponentModel.DesignerSerializationVisibility.Hidden)>  _
    Public Shadows ReadOnly Property Relations() As Global.System.Data.DataRelationCollection
        Get
            Return MyBase.Relations
        End Get
    End Property
    
    <Global.System.Diagnostics.DebuggerNonUserCodeAttribute(),  _
     Global.System.CodeDom.Compiler.GeneratedCodeAttribute("System.Data.Design.TypedDataSetGenerator", "4.0.0.0")>  _
    Protected Overrides Sub InitializeDerivedDataSet()
        Me.BeginInit
        Me.InitClass
        Me.EndInit
    End Sub
    
    <Global.System.Diagnostics.DebuggerNonUserCodeAttribute(),  _
     Global.System.CodeDom.Compiler.GeneratedCodeAttribute("System.Data.Design.TypedDataSetGenerator", "4.0.0.0")>  _
    Public Overrides Function Clone() As Global.System.Data.DataSet
        Dim cln As DatalogDataSet = CType(MyBase.Clone,DatalogDataSet)
        cln.InitVars
        cln.SchemaSerializationMode = Me.SchemaSerializationMode
        Return cln
    End Function
    
    <Global.System.Diagnostics.DebuggerNonUserCodeAttribute(),  _
     Global.System.CodeDom.Compiler.GeneratedCodeAttribute("System.Data.Design.TypedDataSetGenerator", "4.0.0.0")>  _
    Protected Overrides Function ShouldSerializeTables() As Boolean
        Return false
    End Function
    
    <Global.System.Diagnostics.DebuggerNonUserCodeAttribute(),  _
     Global.System.CodeDom.Compiler.GeneratedCodeAttribute("System.Data.Design.TypedDataSetGenerator", "4.0.0.0")>  _
    Protected Overrides Function ShouldSerializeRelations() As Boolean
        Return false
    End Function
    
    <Global.System.Diagnostics.DebuggerNonUserCodeAttribute(),  _
     Global.System.CodeDom.Compiler.GeneratedCodeAttribute("System.Data.Design.TypedDataSetGenerator", "4.0.0.0")>  _
    Protected Overrides Sub ReadXmlSerializable(ByVal reader As Global.System.Xml.XmlReader)
        If (Me.DetermineSchemaSerializationMode(reader) = Global.System.Data.SchemaSerializationMode.IncludeSchema) Then
            Me.Reset
            Dim ds As Global.System.Data.DataSet = New Global.System.Data.DataSet()
            ds.ReadXml(reader)
            If (Not (ds.Tables("Humidity Sensor")) Is Nothing) Then
                MyBase.Tables.Add(New Humidity_SensorDataTable(ds.Tables("Humidity Sensor")))
            End If
            If (Not (ds.Tables("pH Sensor")) Is Nothing) Then
                MyBase.Tables.Add(New pH_SensorDataTable(ds.Tables("pH Sensor")))
            End If
            If (Not (ds.Tables("Temperature Sensor")) Is Nothing) Then
                MyBase.Tables.Add(New Temperature_SensorDataTable(ds.Tables("Temperature Sensor")))
            End If
            Me.DataSetName = ds.DataSetName
            Me.Prefix = ds.Prefix
            Me.Namespace = ds.Namespace
            Me.Locale = ds.Locale
            Me.CaseSensitive = ds.CaseSensitive
            Me.EnforceConstraints = ds.EnforceConstraints
            Me.Merge(ds, false, Global.System.Data.MissingSchemaAction.Add)
            Me.InitVars
        Else
            Me.ReadXml(reader)
            Me.InitVars
        End If
    End Sub
    
    <Global.System.Diagnostics.DebuggerNonUserCodeAttribute(),  _
     Global.System.CodeDom.Compiler.GeneratedCodeAttribute("System.Data.Design.TypedDataSetGenerator", "4.0.0.0")>  _
    Protected Overrides Function GetSchemaSerializable() As Global.System.Xml.Schema.XmlSchema
        Dim stream As Global.System.IO.MemoryStream = New Global.System.IO.MemoryStream()
        Me.WriteXmlSchema(New Global.System.Xml.XmlTextWriter(stream, Nothing))
        stream.Position = 0
        Return Global.System.Xml.Schema.XmlSchema.Read(New Global.System.Xml.XmlTextReader(stream), Nothing)
    End Function
    
    <Global.System.Diagnostics.DebuggerNonUserCodeAttribute(),  _
     Global.System.CodeDom.Compiler.GeneratedCodeAttribute("System.Data.Design.TypedDataSetGenerator", "4.0.0.0")>  _
    Friend Overloads Sub InitVars()
        Me.InitVars(true)
    End Sub
    
    <Global.System.Diagnostics.DebuggerNonUserCodeAttribute(),  _
     Global.System.CodeDom.Compiler.GeneratedCodeAttribute("System.Data.Design.TypedDataSetGenerator", "4.0.0.0")>  _
    Friend Overloads Sub InitVars(ByVal initTable As Boolean)
        Me.tableHumidity_Sensor = CType(MyBase.Tables("Humidity Sensor"),Humidity_SensorDataTable)
        If (initTable = true) Then
            If (Not (Me.tableHumidity_Sensor) Is Nothing) Then
                Me.tableHumidity_Sensor.InitVars
            End If
        End If
        Me.tablepH_Sensor = CType(MyBase.Tables("pH Sensor"),pH_SensorDataTable)
        If (initTable = true) Then
            If (Not (Me.tablepH_Sensor) Is Nothing) Then
                Me.tablepH_Sensor.InitVars
            End If
        End If
        Me.tableTemperature_Sensor = CType(MyBase.Tables("Temperature Sensor"),Temperature_SensorDataTable)
        If (initTable = true) Then
            If (Not (Me.tableTemperature_Sensor) Is Nothing) Then
                Me.tableTemperature_Sensor.InitVars
            End If
        End If
    End Sub
    
    <Global.System.Diagnostics.DebuggerNonUserCodeAttribute(),  _
     Global.System.CodeDom.Compiler.GeneratedCodeAttribute("System.Data.Design.TypedDataSetGenerator", "4.0.0.0")>  _
    Private Sub InitClass()
        Me.DataSetName = "DatalogDataSet"
        Me.Prefix = ""
        Me.Namespace = "http://tempuri.org/DatalogDataSet.xsd"
        Me.EnforceConstraints = true
        Me.SchemaSerializationMode = Global.System.Data.SchemaSerializationMode.IncludeSchema
        Me.tableHumidity_Sensor = New Humidity_SensorDataTable()
        MyBase.Tables.Add(Me.tableHumidity_Sensor)
        Me.tablepH_Sensor = New pH_SensorDataTable()
        MyBase.Tables.Add(Me.tablepH_Sensor)
        Me.tableTemperature_Sensor = New Temperature_SensorDataTable()
        MyBase.Tables.Add(Me.tableTemperature_Sensor)
    End Sub
    
    <Global.System.Diagnostics.DebuggerNonUserCodeAttribute(),  _
     Global.System.CodeDom.Compiler.GeneratedCodeAttribute("System.Data.Design.TypedDataSetGenerator", "4.0.0.0")>  _
    Private Function ShouldSerializeHumidity_Sensor() As Boolean
        Return false
    End Function
    
    <Global.System.Diagnostics.DebuggerNonUserCodeAttribute(),  _
     Global.System.CodeDom.Compiler.GeneratedCodeAttribute("System.Data.Design.TypedDataSetGenerator", "4.0.0.0")>  _
    Private Function ShouldSerializepH_Sensor() As Boolean
        Return false
    End Function
    
    <Global.System.Diagnostics.DebuggerNonUserCodeAttribute(),  _
     Global.System.CodeDom.Compiler.GeneratedCodeAttribute("System.Data.Design.TypedDataSetGenerator", "4.0.0.0")>  _
    Private Function ShouldSerializeTemperature_Sensor() As Boolean
        Return false
    End Function
    
    <Global.System.Diagnostics.DebuggerNonUserCodeAttribute(),  _
     Global.System.CodeDom.Compiler.GeneratedCodeAttribute("System.Data.Design.TypedDataSetGenerator", "4.0.0.0")>  _
    Private Sub SchemaChanged(ByVal sender As Object, ByVal e As Global.System.ComponentModel.CollectionChangeEventArgs)
        If (e.Action = Global.System.ComponentModel.CollectionChangeAction.Remove) Then
            Me.InitVars
        End If
    End Sub
    
    <Global.System.Diagnostics.DebuggerNonUserCodeAttribute(),  _
     Global.System.CodeDom.Compiler.GeneratedCodeAttribute("System.Data.Design.TypedDataSetGenerator", "4.0.0.0")>  _
    Public Shared Function GetTypedDataSetSchema(ByVal xs As Global.System.Xml.Schema.XmlSchemaSet) As Global.System.Xml.Schema.XmlSchemaComplexType
        Dim ds As DatalogDataSet = New DatalogDataSet()
        Dim type As Global.System.Xml.Schema.XmlSchemaComplexType = New Global.System.Xml.Schema.XmlSchemaComplexType()
        Dim sequence As Global.System.Xml.Schema.XmlSchemaSequence = New Global.System.Xml.Schema.XmlSchemaSequence()
        Dim any As Global.System.Xml.Schema.XmlSchemaAny = New Global.System.Xml.Schema.XmlSchemaAny()
        any.Namespace = ds.Namespace
        sequence.Items.Add(any)
        type.Particle = sequence
        Dim dsSchema As Global.System.Xml.Schema.XmlSchema = ds.GetSchemaSerializable
        If xs.Contains(dsSchema.TargetNamespace) Then
            Dim s1 As Global.System.IO.MemoryStream = New Global.System.IO.MemoryStream()
            Dim s2 As Global.System.IO.MemoryStream = New Global.System.IO.MemoryStream()
            Try 
                Dim schema As Global.System.Xml.Schema.XmlSchema = Nothing
                dsSchema.Write(s1)
                Dim schemas As Global.System.Collections.IEnumerator = xs.Schemas(dsSchema.TargetNamespace).GetEnumerator
                Do While schemas.MoveNext
                    schema = CType(schemas.Current,Global.System.Xml.Schema.XmlSchema)
                    s2.SetLength(0)
                    schema.Write(s2)
                    If (s1.Length = s2.Length) Then
                        s1.Position = 0
                        s2.Position = 0
                        
                        Do While ((s1.Position <> s1.Length)  _
                                    AndAlso (s1.ReadByte = s2.ReadByte))
                            
                            
                        Loop
                        If (s1.Position = s1.Length) Then
                            Return type
                        End If
                    End If
                    
                Loop
            Finally
                If (Not (s1) Is Nothing) Then
                    s1.Close
                End If
                If (Not (s2) Is Nothing) Then
                    s2.Close
                End If
            End Try
        End If
        xs.Add(dsSchema)
        Return type
    End Function
    
    <Global.System.CodeDom.Compiler.GeneratedCodeAttribute("System.Data.Design.TypedDataSetGenerator", "4.0.0.0")>  _
    Public Delegate Sub Humidity_SensorRowChangeEventHandler(ByVal sender As Object, ByVal e As Humidity_SensorRowChangeEvent)
    
    <Global.System.CodeDom.Compiler.GeneratedCodeAttribute("System.Data.Design.TypedDataSetGenerator", "4.0.0.0")>  _
    Public Delegate Sub pH_SensorRowChangeEventHandler(ByVal sender As Object, ByVal e As pH_SensorRowChangeEvent)
    
    <Global.System.CodeDom.Compiler.GeneratedCodeAttribute("System.Data.Design.TypedDataSetGenerator", "4.0.0.0")>  _
    Public Delegate Sub Temperature_SensorRowChangeEventHandler(ByVal sender As Object, ByVal e As Temperature_SensorRowChangeEvent)
    
    '''<summary>
    '''Represents the strongly named DataTable class.
    '''</summary>
    <Global.System.Serializable(),  _
     Global.System.Xml.Serialization.XmlSchemaProviderAttribute("GetTypedTableSchema")>  _
    Partial Public Class Humidity_SensorDataTable
        Inherits Global.System.Data.TypedTableBase(Of Humidity_SensorRow)
        
        Private _columnDate_Time As Global.System.Data.DataColumn
        
        Private columnValue As Global.System.Data.DataColumn
        
        <Global.System.Diagnostics.DebuggerNonUserCodeAttribute(),  _
         Global.System.CodeDom.Compiler.GeneratedCodeAttribute("System.Data.Design.TypedDataSetGenerator", "4.0.0.0")>  _
        Public Sub New()
            MyBase.New
            Me.TableName = "Humidity Sensor"
            Me.BeginInit
            Me.InitClass
            Me.EndInit
        End Sub
        
        <Global.System.Diagnostics.DebuggerNonUserCodeAttribute(),  _
         Global.System.CodeDom.Compiler.GeneratedCodeAttribute("System.Data.Design.TypedDataSetGenerator", "4.0.0.0")>  _
        Friend Sub New(ByVal table As Global.System.Data.DataTable)
            MyBase.New
            Me.TableName = table.TableName
            If (table.CaseSensitive <> table.DataSet.CaseSensitive) Then
                Me.CaseSensitive = table.CaseSensitive
            End If
            If (table.Locale.ToString <> table.DataSet.Locale.ToString) Then
                Me.Locale = table.Locale
            End If
            If (table.Namespace <> table.DataSet.Namespace) Then
                Me.Namespace = table.Namespace
            End If
            Me.Prefix = table.Prefix
            Me.MinimumCapacity = table.MinimumCapacity
        End Sub
        
        <Global.System.Diagnostics.DebuggerNonUserCodeAttribute(),  _
         Global.System.CodeDom.Compiler.GeneratedCodeAttribute("System.Data.Design.TypedDataSetGenerator", "4.0.0.0")>  _
        Protected Sub New(ByVal info As Global.System.Runtime.Serialization.SerializationInfo, ByVal context As Global.System.Runtime.Serialization.StreamingContext)
            MyBase.New(info, context)
            Me.InitVars
        End Sub
        
        <Global.System.Diagnostics.DebuggerNonUserCodeAttribute(),  _
         Global.System.CodeDom.Compiler.GeneratedCodeAttribute("System.Data.Design.TypedDataSetGenerator", "4.0.0.0")>  _
        Public ReadOnly Property _Date_TimeColumn() As Global.System.Data.DataColumn
            Get
                Return Me._columnDate_Time
            End Get
        End Property
        
        <Global.System.Diagnostics.DebuggerNonUserCodeAttribute(),  _
         Global.System.CodeDom.Compiler.GeneratedCodeAttribute("System.Data.Design.TypedDataSetGenerator", "4.0.0.0")>  _
        Public ReadOnly Property ValueColumn() As Global.System.Data.DataColumn
            Get
                Return Me.columnValue
            End Get
        End Property
        
        <Global.System.Diagnostics.DebuggerNonUserCodeAttribute(),  _
         Global.System.CodeDom.Compiler.GeneratedCodeAttribute("System.Data.Design.TypedDataSetGenerator", "4.0.0.0"),  _
         Global.System.ComponentModel.Browsable(false)>  _
        Public ReadOnly Property Count() As Integer
            Get
                Return Me.Rows.Count
            End Get
        End Property
        
        <Global.System.Diagnostics.DebuggerNonUserCodeAttribute(),  _
         Global.System.CodeDom.Compiler.GeneratedCodeAttribute("System.Data.Design.TypedDataSetGenerator", "4.0.0.0")>  _
        Public Default ReadOnly Property Item(ByVal index As Integer) As Humidity_SensorRow
            Get
                Return CType(Me.Rows(index),Humidity_SensorRow)
            End Get
        End Property
        
        <Global.System.CodeDom.Compiler.GeneratedCodeAttribute("System.Data.Design.TypedDataSetGenerator", "4.0.0.0")>  _
        Public Event Humidity_SensorRowChanging As Humidity_SensorRowChangeEventHandler
        
        <Global.System.CodeDom.Compiler.GeneratedCodeAttribute("System.Data.Design.TypedDataSetGenerator", "4.0.0.0")>  _
        Public Event Humidity_SensorRowChanged As Humidity_SensorRowChangeEventHandler
        
        <Global.System.CodeDom.Compiler.GeneratedCodeAttribute("System.Data.Design.TypedDataSetGenerator", "4.0.0.0")>  _
        Public Event Humidity_SensorRowDeleting As Humidity_SensorRowChangeEventHandler
        
        <Global.System.CodeDom.Compiler.GeneratedCodeAttribute("System.Data.Design.TypedDataSetGenerator", "4.0.0.0")>  _
        Public Event Humidity_SensorRowDeleted As Humidity_SensorRowChangeEventHandler
        
        <Global.System.Diagnostics.DebuggerNonUserCodeAttribute(),  _
         Global.System.CodeDom.Compiler.GeneratedCodeAttribute("System.Data.Design.TypedDataSetGenerator", "4.0.0.0")>  _
        Public Overloads Sub AddHumidity_SensorRow(ByVal row As Humidity_SensorRow)
            Me.Rows.Add(row)
        End Sub
        
        <Global.System.Diagnostics.DebuggerNonUserCodeAttribute(),  _
         Global.System.CodeDom.Compiler.GeneratedCodeAttribute("System.Data.Design.TypedDataSetGenerator", "4.0.0.0")>  _
        Public Overloads Function AddHumidity_SensorRow(ByVal _Date_Time As Date, ByVal Value As Integer) As Humidity_SensorRow
            Dim rowHumidity_SensorRow As Humidity_SensorRow = CType(Me.NewRow,Humidity_SensorRow)
            Dim columnValuesArray() As Object = New Object() {_Date_Time, Value}
            rowHumidity_SensorRow.ItemArray = columnValuesArray
            Me.Rows.Add(rowHumidity_SensorRow)
            Return rowHumidity_SensorRow
        End Function
        
        <Global.System.Diagnostics.DebuggerNonUserCodeAttribute(),  _
         Global.System.CodeDom.Compiler.GeneratedCodeAttribute("System.Data.Design.TypedDataSetGenerator", "4.0.0.0")>  _
        Public Overrides Function Clone() As Global.System.Data.DataTable
            Dim cln As Humidity_SensorDataTable = CType(MyBase.Clone,Humidity_SensorDataTable)
            cln.InitVars
            Return cln
        End Function
        
        <Global.System.Diagnostics.DebuggerNonUserCodeAttribute(),  _
         Global.System.CodeDom.Compiler.GeneratedCodeAttribute("System.Data.Design.TypedDataSetGenerator", "4.0.0.0")>  _
        Protected Overrides Function CreateInstance() As Global.System.Data.DataTable
            Return New Humidity_SensorDataTable()
        End Function
        
        <Global.System.Diagnostics.DebuggerNonUserCodeAttribute(),  _
         Global.System.CodeDom.Compiler.GeneratedCodeAttribute("System.Data.Design.TypedDataSetGenerator", "4.0.0.0")>  _
        Friend Sub InitVars()
            Me._columnDate_Time = MyBase.Columns("Date/Time")
            Me.columnValue = MyBase.Columns("Value")
        End Sub
        
        <Global.System.Diagnostics.DebuggerNonUserCodeAttribute(),  _
         Global.System.CodeDom.Compiler.GeneratedCodeAttribute("System.Data.Design.TypedDataSetGenerator", "4.0.0.0")>  _
        Private Sub InitClass()
            Me._columnDate_Time = New Global.System.Data.DataColumn("Date/Time", GetType(Date), Nothing, Global.System.Data.MappingType.Element)
            Me._columnDate_Time.ExtendedProperties.Add("Generator_ColumnVarNameInTable", "_columnDate_Time")
            Me._columnDate_Time.ExtendedProperties.Add("Generator_UserColumnName", "Date/Time")
            MyBase.Columns.Add(Me._columnDate_Time)
            Me.columnValue = New Global.System.Data.DataColumn("Value", GetType(Integer), Nothing, Global.System.Data.MappingType.Element)
            MyBase.Columns.Add(Me.columnValue)
        End Sub
        
        <Global.System.Diagnostics.DebuggerNonUserCodeAttribute(),  _
         Global.System.CodeDom.Compiler.GeneratedCodeAttribute("System.Data.Design.TypedDataSetGenerator", "4.0.0.0")>  _
        Public Function NewHumidity_SensorRow() As Humidity_SensorRow
            Return CType(Me.NewRow,Humidity_SensorRow)
        End Function
        
        <Global.System.Diagnostics.DebuggerNonUserCodeAttribute(),  _
         Global.System.CodeDom.Compiler.GeneratedCodeAttribute("System.Data.Design.TypedDataSetGenerator", "4.0.0.0")>  _
        Protected Overrides Function NewRowFromBuilder(ByVal builder As Global.System.Data.DataRowBuilder) As Global.System.Data.DataRow
            Return New Humidity_SensorRow(builder)
        End Function
        
        <Global.System.Diagnostics.DebuggerNonUserCodeAttribute(),  _
         Global.System.CodeDom.Compiler.GeneratedCodeAttribute("System.Data.Design.TypedDataSetGenerator", "4.0.0.0")>  _
        Protected Overrides Function GetRowType() As Global.System.Type
            Return GetType(Humidity_SensorRow)
        End Function
        
        <Global.System.Diagnostics.DebuggerNonUserCodeAttribute(),  _
         Global.System.CodeDom.Compiler.GeneratedCodeAttribute("System.Data.Design.TypedDataSetGenerator", "4.0.0.0")>  _
        Protected Overrides Sub OnRowChanged(ByVal e As Global.System.Data.DataRowChangeEventArgs)
            MyBase.OnRowChanged(e)
            If (Not (Me.Humidity_SensorRowChangedEvent) Is Nothing) Then
                RaiseEvent Humidity_SensorRowChanged(Me, New Humidity_SensorRowChangeEvent(CType(e.Row,Humidity_SensorRow), e.Action))
            End If
        End Sub
        
        <Global.System.Diagnostics.DebuggerNonUserCodeAttribute(),  _
         Global.System.CodeDom.Compiler.GeneratedCodeAttribute("System.Data.Design.TypedDataSetGenerator", "4.0.0.0")>  _
        Protected Overrides Sub OnRowChanging(ByVal e As Global.System.Data.DataRowChangeEventArgs)
            MyBase.OnRowChanging(e)
            If (Not (Me.Humidity_SensorRowChangingEvent) Is Nothing) Then
                RaiseEvent Humidity_SensorRowChanging(Me, New Humidity_SensorRowChangeEvent(CType(e.Row,Humidity_SensorRow), e.Action))
            End If
        End Sub
        
        <Global.System.Diagnostics.DebuggerNonUserCodeAttribute(),  _
         Global.System.CodeDom.Compiler.GeneratedCodeAttribute("System.Data.Design.TypedDataSetGenerator", "4.0.0.0")>  _
        Protected Overrides Sub OnRowDeleted(ByVal e As Global.System.Data.DataRowChangeEventArgs)
            MyBase.OnRowDeleted(e)
            If (Not (Me.Humidity_SensorRowDeletedEvent) Is Nothing) Then
                RaiseEvent Humidity_SensorRowDeleted(Me, New Humidity_SensorRowChangeEvent(CType(e.Row,Humidity_SensorRow), e.Action))
            End If
        End Sub
        
        <Global.System.Diagnostics.DebuggerNonUserCodeAttribute(),  _
         Global.System.CodeDom.Compiler.GeneratedCodeAttribute("System.Data.Design.TypedDataSetGenerator", "4.0.0.0")>  _
        Protected Overrides Sub OnRowDeleting(ByVal e As Global.System.Data.DataRowChangeEventArgs)
            MyBase.OnRowDeleting(e)
            If (Not (Me.Humidity_SensorRowDeletingEvent) Is Nothing) Then
                RaiseEvent Humidity_SensorRowDeleting(Me, New Humidity_SensorRowChangeEvent(CType(e.Row,Humidity_SensorRow), e.Action))
            End If
        End Sub
        
        <Global.System.Diagnostics.DebuggerNonUserCodeAttribute(),  _
         Global.System.CodeDom.Compiler.GeneratedCodeAttribute("System.Data.Design.TypedDataSetGenerator", "4.0.0.0")>  _
        Public Sub RemoveHumidity_SensorRow(ByVal row As Humidity_SensorRow)
            Me.Rows.Remove(row)
        End Sub
        
        <Global.System.Diagnostics.DebuggerNonUserCodeAttribute(),  _
         Global.System.CodeDom.Compiler.GeneratedCodeAttribute("System.Data.Design.TypedDataSetGenerator", "4.0.0.0")>  _
        Public Shared Function GetTypedTableSchema(ByVal xs As Global.System.Xml.Schema.XmlSchemaSet) As Global.System.Xml.Schema.XmlSchemaComplexType
            Dim type As Global.System.Xml.Schema.XmlSchemaComplexType = New Global.System.Xml.Schema.XmlSchemaComplexType()
            Dim sequence As Global.System.Xml.Schema.XmlSchemaSequence = New Global.System.Xml.Schema.XmlSchemaSequence()
            Dim ds As DatalogDataSet = New DatalogDataSet()
            Dim any1 As Global.System.Xml.Schema.XmlSchemaAny = New Global.System.Xml.Schema.XmlSchemaAny()
            any1.Namespace = "http://www.w3.org/2001/XMLSchema"
            any1.MinOccurs = New Decimal(0)
            any1.MaxOccurs = Decimal.MaxValue
            any1.ProcessContents = Global.System.Xml.Schema.XmlSchemaContentProcessing.Lax
            sequence.Items.Add(any1)
            Dim any2 As Global.System.Xml.Schema.XmlSchemaAny = New Global.System.Xml.Schema.XmlSchemaAny()
            any2.Namespace = "urn:schemas-microsoft-com:xml-diffgram-v1"
            any2.MinOccurs = New Decimal(1)
            any2.ProcessContents = Global.System.Xml.Schema.XmlSchemaContentProcessing.Lax
            sequence.Items.Add(any2)
            Dim attribute1 As Global.System.Xml.Schema.XmlSchemaAttribute = New Global.System.Xml.Schema.XmlSchemaAttribute()
            attribute1.Name = "namespace"
            attribute1.FixedValue = ds.Namespace
            type.Attributes.Add(attribute1)
            Dim attribute2 As Global.System.Xml.Schema.XmlSchemaAttribute = New Global.System.Xml.Schema.XmlSchemaAttribute()
            attribute2.Name = "tableTypeName"
            attribute2.FixedValue = "Humidity_SensorDataTable"
            type.Attributes.Add(attribute2)
            type.Particle = sequence
            Dim dsSchema As Global.System.Xml.Schema.XmlSchema = ds.GetSchemaSerializable
            If xs.Contains(dsSchema.TargetNamespace) Then
                Dim s1 As Global.System.IO.MemoryStream = New Global.System.IO.MemoryStream()
                Dim s2 As Global.System.IO.MemoryStream = New Global.System.IO.MemoryStream()
                Try 
                    Dim schema As Global.System.Xml.Schema.XmlSchema = Nothing
                    dsSchema.Write(s1)
                    Dim schemas As Global.System.Collections.IEnumerator = xs.Schemas(dsSchema.TargetNamespace).GetEnumerator
                    Do While schemas.MoveNext
                        schema = CType(schemas.Current,Global.System.Xml.Schema.XmlSchema)
                        s2.SetLength(0)
                        schema.Write(s2)
                        If (s1.Length = s2.Length) Then
                            s1.Position = 0
                            s2.Position = 0
                            
                            Do While ((s1.Position <> s1.Length)  _
                                        AndAlso (s1.ReadByte = s2.ReadByte))
                                
                                
                            Loop
                            If (s1.Position = s1.Length) Then
                                Return type
                            End If
                        End If
                        
                    Loop
                Finally
                    If (Not (s1) Is Nothing) Then
                        s1.Close
                    End If
                    If (Not (s2) Is Nothing) Then
                        s2.Close
                    End If
                End Try
            End If
            xs.Add(dsSchema)
            Return type
        End Function
    End Class
    
    '''<summary>
    '''Represents the strongly named DataTable class.
    '''</summary>
    <Global.System.Serializable(),  _
     Global.System.Xml.Serialization.XmlSchemaProviderAttribute("GetTypedTableSchema")>  _
    Partial Public Class pH_SensorDataTable
        Inherits Global.System.Data.TypedTableBase(Of pH_SensorRow)
        
        Private _columnDate_Time As Global.System.Data.DataColumn
        
        Private columnValue As Global.System.Data.DataColumn
        
        <Global.System.Diagnostics.DebuggerNonUserCodeAttribute(),  _
         Global.System.CodeDom.Compiler.GeneratedCodeAttribute("System.Data.Design.TypedDataSetGenerator", "4.0.0.0")>  _
        Public Sub New()
            MyBase.New
            Me.TableName = "pH Sensor"
            Me.BeginInit
            Me.InitClass
            Me.EndInit
        End Sub
        
        <Global.System.Diagnostics.DebuggerNonUserCodeAttribute(),  _
         Global.System.CodeDom.Compiler.GeneratedCodeAttribute("System.Data.Design.TypedDataSetGenerator", "4.0.0.0")>  _
        Friend Sub New(ByVal table As Global.System.Data.DataTable)
            MyBase.New
            Me.TableName = table.TableName
            If (table.CaseSensitive <> table.DataSet.CaseSensitive) Then
                Me.CaseSensitive = table.CaseSensitive
            End If
            If (table.Locale.ToString <> table.DataSet.Locale.ToString) Then
                Me.Locale = table.Locale
            End If
            If (table.Namespace <> table.DataSet.Namespace) Then
                Me.Namespace = table.Namespace
            End If
            Me.Prefix = table.Prefix
            Me.MinimumCapacity = table.MinimumCapacity
        End Sub
        
        <Global.System.Diagnostics.DebuggerNonUserCodeAttribute(),  _
         Global.System.CodeDom.Compiler.GeneratedCodeAttribute("System.Data.Design.TypedDataSetGenerator", "4.0.0.0")>  _
        Protected Sub New(ByVal info As Global.System.Runtime.Serialization.SerializationInfo, ByVal context As Global.System.Runtime.Serialization.StreamingContext)
            MyBase.New(info, context)
            Me.InitVars
        End Sub
        
        <Global.System.Diagnostics.DebuggerNonUserCodeAttribute(),  _
         Global.System.CodeDom.Compiler.GeneratedCodeAttribute("System.Data.Design.TypedDataSetGenerator", "4.0.0.0")>  _
        Public ReadOnly Property _Date_TimeColumn() As Global.System.Data.DataColumn
            Get
                Return Me._columnDate_Time
            End Get
        End Property
        
        <Global.System.Diagnostics.DebuggerNonUserCodeAttribute(),  _
         Global.System.CodeDom.Compiler.GeneratedCodeAttribute("System.Data.Design.TypedDataSetGenerator", "4.0.0.0")>  _
        Public ReadOnly Property ValueColumn() As Global.System.Data.DataColumn
            Get
                Return Me.columnValue
            End Get
        End Property
        
        <Global.System.Diagnostics.DebuggerNonUserCodeAttribute(),  _
         Global.System.CodeDom.Compiler.GeneratedCodeAttribute("System.Data.Design.TypedDataSetGenerator", "4.0.0.0"),  _
         Global.System.ComponentModel.Browsable(false)>  _
        Public ReadOnly Property Count() As Integer
            Get
                Return Me.Rows.Count
            End Get
        End Property
        
        <Global.System.Diagnostics.DebuggerNonUserCodeAttribute(),  _
         Global.System.CodeDom.Compiler.GeneratedCodeAttribute("System.Data.Design.TypedDataSetGenerator", "4.0.0.0")>  _
        Public Default ReadOnly Property Item(ByVal index As Integer) As pH_SensorRow
            Get
                Return CType(Me.Rows(index),pH_SensorRow)
            End Get
        End Property
        
        <Global.System.CodeDom.Compiler.GeneratedCodeAttribute("System.Data.Design.TypedDataSetGenerator", "4.0.0.0")>  _
        Public Event pH_SensorRowChanging As pH_SensorRowChangeEventHandler
        
        <Global.System.CodeDom.Compiler.GeneratedCodeAttribute("System.Data.Design.TypedDataSetGenerator", "4.0.0.0")>  _
        Public Event pH_SensorRowChanged As pH_SensorRowChangeEventHandler
        
        <Global.System.CodeDom.Compiler.GeneratedCodeAttribute("System.Data.Design.TypedDataSetGenerator", "4.0.0.0")>  _
        Public Event pH_SensorRowDeleting As pH_SensorRowChangeEventHandler
        
        <Global.System.CodeDom.Compiler.GeneratedCodeAttribute("System.Data.Design.TypedDataSetGenerator", "4.0.0.0")>  _
        Public Event pH_SensorRowDeleted As pH_SensorRowChangeEventHandler
        
        <Global.System.Diagnostics.DebuggerNonUserCodeAttribute(),  _
         Global.System.CodeDom.Compiler.GeneratedCodeAttribute("System.Data.Design.TypedDataSetGenerator", "4.0.0.0")>  _
        Public Overloads Sub AddpH_SensorRow(ByVal row As pH_SensorRow)
            Me.Rows.Add(row)
        End Sub
        
        <Global.System.Diagnostics.DebuggerNonUserCodeAttribute(),  _
         Global.System.CodeDom.Compiler.GeneratedCodeAttribute("System.Data.Design.TypedDataSetGenerator", "4.0.0.0")>  _
        Public Overloads Function AddpH_SensorRow(ByVal _Date_Time As Date, ByVal Value As Double) As pH_SensorRow
            Dim rowpH_SensorRow As pH_SensorRow = CType(Me.NewRow,pH_SensorRow)
            Dim columnValuesArray() As Object = New Object() {_Date_Time, Value}
            rowpH_SensorRow.ItemArray = columnValuesArray
            Me.Rows.Add(rowpH_SensorRow)
            Return rowpH_SensorRow
        End Function
        
        <Global.System.Diagnostics.DebuggerNonUserCodeAttribute(),  _
         Global.System.CodeDom.Compiler.GeneratedCodeAttribute("System.Data.Design.TypedDataSetGenerator", "4.0.0.0")>  _
        Public Overrides Function Clone() As Global.System.Data.DataTable
            Dim cln As pH_SensorDataTable = CType(MyBase.Clone,pH_SensorDataTable)
            cln.InitVars
            Return cln
        End Function
        
        <Global.System.Diagnostics.DebuggerNonUserCodeAttribute(),  _
         Global.System.CodeDom.Compiler.GeneratedCodeAttribute("System.Data.Design.TypedDataSetGenerator", "4.0.0.0")>  _
        Protected Overrides Function CreateInstance() As Global.System.Data.DataTable
            Return New pH_SensorDataTable()
        End Function
        
        <Global.System.Diagnostics.DebuggerNonUserCodeAttribute(),  _
         Global.System.CodeDom.Compiler.GeneratedCodeAttribute("System.Data.Design.TypedDataSetGenerator", "4.0.0.0")>  _
        Friend Sub InitVars()
            Me._columnDate_Time = MyBase.Columns("Date/Time")
            Me.columnValue = MyBase.Columns("Value")
        End Sub
        
        <Global.System.Diagnostics.DebuggerNonUserCodeAttribute(),  _
         Global.System.CodeDom.Compiler.GeneratedCodeAttribute("System.Data.Design.TypedDataSetGenerator", "4.0.0.0")>  _
        Private Sub InitClass()
            Me._columnDate_Time = New Global.System.Data.DataColumn("Date/Time", GetType(Date), Nothing, Global.System.Data.MappingType.Element)
            Me._columnDate_Time.ExtendedProperties.Add("Generator_ColumnVarNameInTable", "_columnDate_Time")
            Me._columnDate_Time.ExtendedProperties.Add("Generator_UserColumnName", "Date/Time")
            MyBase.Columns.Add(Me._columnDate_Time)
            Me.columnValue = New Global.System.Data.DataColumn("Value", GetType(Double), Nothing, Global.System.Data.MappingType.Element)
            MyBase.Columns.Add(Me.columnValue)
            Me._columnDate_Time.AllowDBNull = false
        End Sub
        
        <Global.System.Diagnostics.DebuggerNonUserCodeAttribute(),  _
         Global.System.CodeDom.Compiler.GeneratedCodeAttribute("System.Data.Design.TypedDataSetGenerator", "4.0.0.0")>  _
        Public Function NewpH_SensorRow() As pH_SensorRow
            Return CType(Me.NewRow,pH_SensorRow)
        End Function
        
        <Global.System.Diagnostics.DebuggerNonUserCodeAttribute(),  _
         Global.System.CodeDom.Compiler.GeneratedCodeAttribute("System.Data.Design.TypedDataSetGenerator", "4.0.0.0")>  _
        Protected Overrides Function NewRowFromBuilder(ByVal builder As Global.System.Data.DataRowBuilder) As Global.System.Data.DataRow
            Return New pH_SensorRow(builder)
        End Function
        
        <Global.System.Diagnostics.DebuggerNonUserCodeAttribute(),  _
         Global.System.CodeDom.Compiler.GeneratedCodeAttribute("System.Data.Design.TypedDataSetGenerator", "4.0.0.0")>  _
        Protected Overrides Function GetRowType() As Global.System.Type
            Return GetType(pH_SensorRow)
        End Function
        
        <Global.System.Diagnostics.DebuggerNonUserCodeAttribute(),  _
         Global.System.CodeDom.Compiler.GeneratedCodeAttribute("System.Data.Design.TypedDataSetGenerator", "4.0.0.0")>  _
        Protected Overrides Sub OnRowChanged(ByVal e As Global.System.Data.DataRowChangeEventArgs)
            MyBase.OnRowChanged(e)
            If (Not (Me.pH_SensorRowChangedEvent) Is Nothing) Then
                RaiseEvent pH_SensorRowChanged(Me, New pH_SensorRowChangeEvent(CType(e.Row,pH_SensorRow), e.Action))
            End If
        End Sub
        
        <Global.System.Diagnostics.DebuggerNonUserCodeAttribute(),  _
         Global.System.CodeDom.Compiler.GeneratedCodeAttribute("System.Data.Design.TypedDataSetGenerator", "4.0.0.0")>  _
        Protected Overrides Sub OnRowChanging(ByVal e As Global.System.Data.DataRowChangeEventArgs)
            MyBase.OnRowChanging(e)
            If (Not (Me.pH_SensorRowChangingEvent) Is Nothing) Then
                RaiseEvent pH_SensorRowChanging(Me, New pH_SensorRowChangeEvent(CType(e.Row,pH_SensorRow), e.Action))
            End If
        End Sub
        
        <Global.System.Diagnostics.DebuggerNonUserCodeAttribute(),  _
         Global.System.CodeDom.Compiler.GeneratedCodeAttribute("System.Data.Design.TypedDataSetGenerator", "4.0.0.0")>  _
        Protected Overrides Sub OnRowDeleted(ByVal e As Global.System.Data.DataRowChangeEventArgs)
            MyBase.OnRowDeleted(e)
            If (Not (Me.pH_SensorRowDeletedEvent) Is Nothing) Then
                RaiseEvent pH_SensorRowDeleted(Me, New pH_SensorRowChangeEvent(CType(e.Row,pH_SensorRow), e.Action))
            End If
        End Sub
        
        <Global.System.Diagnostics.DebuggerNonUserCodeAttribute(),  _
         Global.System.CodeDom.Compiler.GeneratedCodeAttribute("System.Data.Design.TypedDataSetGenerator", "4.0.0.0")>  _
        Protected Overrides Sub OnRowDeleting(ByVal e As Global.System.Data.DataRowChangeEventArgs)
            MyBase.OnRowDeleting(e)
            If (Not (Me.pH_SensorRowDeletingEvent) Is Nothing) Then
                RaiseEvent pH_SensorRowDeleting(Me, New pH_SensorRowChangeEvent(CType(e.Row,pH_SensorRow), e.Action))
            End If
        End Sub
        
        <Global.System.Diagnostics.DebuggerNonUserCodeAttribute(),  _
         Global.System.CodeDom.Compiler.GeneratedCodeAttribute("System.Data.Design.TypedDataSetGenerator", "4.0.0.0")>  _
        Public Sub RemovepH_SensorRow(ByVal row As pH_SensorRow)
            Me.Rows.Remove(row)
        End Sub
    End Class
End Namespace

Imports System.ServiceProcess
Imports System.Reflection.Assembly
Imports PluginMGMT
Imports Notifications

Public Class HealthMonitor
    Inherits System.ServiceProcess.ServiceBase

#Region " Codice generato da Progettazione componenti "

    Public Sub New()
        MyBase.New()

        ' Chiamata richiesta da Progettazione componenti.
        InitializeComponent()

        ' Aggiungere le eventuali istruzioni di inizializzazione dopo la chiamata a InitializeComponent()

    End Sub

    'UserService esegue l'override del metodo Dispose per pulire l'elenco dei componenti.
    Protected Overloads Overrides Sub Dispose(ByVal disposing As Boolean)
        If disposing Then
            If Not (components Is Nothing) Then
                components.Dispose()
            End If
        End If
        MyBase.Dispose(disposing)
    End Sub

    ' Punto di ingresso principale del processo
    <MTAThread()> _
    Shared Sub Main()
        Dim ServicesToRun() As System.ServiceProcess.ServiceBase

        ' All'interno di uno stesso processo � possibile eseguire pi� servizi di Windows NT.
        ' Per aggiungere un servizio al processo, modificare la riga che segue in modo
        ' da creare un secondo oggetto servizio. Ad esempio,
        '
        '   ServicesToRun = New System.ServiceProcess.ServiceBase () {New Service1, New MySecondUserService}
        '
        ServicesToRun = New System.ServiceProcess.ServiceBase() {New HealthMonitor}

        System.ServiceProcess.ServiceBase.Run(ServicesToRun)
    End Sub

    'Richiesto da Progettazione componenti
    Private components As System.ComponentModel.IContainer

    ' NOTA: la procedura che segue � richiesta da Progettazione componenti
    ' Pu� essere modificata in Progettazione componenti.  
    ' Non modificarla nell'editor del codice.
    <System.Diagnostics.DebuggerStepThrough()> Private Sub InitializeComponent()
        '
        'HealthMonitor
        '
        Me.ServiceName = "HealthMonitor"

    End Sub

#End Region

    'Dim CheckEventThread As New System.Threading.Thread(AddressOf SubmitCheckEvent)
    Private WithEvents PluginMgmtObj As New PluginEngine
    Public Version As String


#Region "Check Start-Stop Service"

    Protected Overrides Sub OnStart(ByVal args() As String)
        Dim i As Integer
        Dim message As String
        Try
            'Get version information
            Version = System.Reflection.Assembly.GetExecutingAssembly.GetName.Version.ToString
            message = "Starting HealthMonitor " & Version

            Dim Arguments As [String]() = Environment.GetCommandLineArgs()
            Dim Argument As String
            'MsgBox([String].Join(", ", arguments))
            For Each Argument In Arguments
                If UCase(Argument) = "-V" Or UCase(Argument) = "-VERBOSE" Then
                    VerboseLogging = True
                    message &= " (enable verbose logging)"
                End If
            Next

            TextFileLogging(message)
            If Not EventLog.SourceExists("HealthMonitor") Then
                EventLog.CreateEventSource("HealthMonitor", "Application")
            End If

            If NotifProcEngObj.ReadParameters = False Then
                NotifProcEngObj.LoadDefaultParameters()
            End If
            If EmailNotifObj.ReadParameters() = False Then
                EmailNotifObj.LoadDefaultParameters()
            End If
            If SMSNotifObj.ReadParameters() = False Then
                SMSNotifObj.LoadDefaultParameters()
            End If
            If NETSENDNotifObj.ReadParameters() = False Then
                NETSENDNotifObj.LoadDefaultParameters()
            End If
            If ScriptNotifObj.ReadParameters() = False Then
                ScriptNotifObj.LoadDefaultParameters()
            End If

            PluginMgmtObj.LoadPlugins()
            For i = 0 To PluginMgmtObj.plugins.Count - 1
                PluginMgmtObj.plugins.item(i).VerboseLogging = VerboseLogging
                PluginMgmtObj.plugins.item(i).StartCheck()
            Next
        Catch ex As Exception
            EventLogging(ex.ToString, "Medium", 204)
        End Try
    End Sub

    Protected Overrides Sub OnStop()
        Try
            Dim i As Integer
            TextFileLogging("Stopping HealthMonitor " & Version)

            PluginMgmtObj.LoadPlugins()
            For i = 0 To PluginMgmtObj.plugins.Count - 1
                PluginMgmtObj.plugins.item(i).StopCheck()
            Next
            'If EventCheckEnabled = True Then
            '    CheckEventThread.Suspend()
            'End If
            TextFileLogging("HealthMonitor " & Version & " service has been stopped ")
        Catch ex As Exception
            EventLogging(ex.ToString, "Medium", 205)
        End Try
    End Sub

#End Region

#Region "Other Function"

    Private Function GetHostname()
        Try
            Dim objWMIService, objHosts, objHostName
            Dim strComputer As String = "."
            objWMIService = GetObject("winmgmts:" & "{impersonationLevel=impersonate}!\\" & strComputer & "\root\cimv2")
            objHosts = objWMIService.ExecQuery("Select * from Win32_ComputerSystem")
            For Each objHostName In objHosts
                Return objHostName.name
            Next
        Catch ex As Exception
            EventLogging(ex.ToString, "Medium", 206)
        End Try
    End Function

    Protected Overrides Sub OnCustomCommand(ByVal command As Integer)
        Try
            Select Case command
                Case 128
                    'SubmitCheckDisk()
                Case 129
                    'This is a workaround because launching SubminCheckServices thrown an exception
                    'CheckServiceTimer.Stop()
                    'CheckServiceTimer.Interval = 1
                    'CheckServiceTimer.Start()
                Case 130
                    'SubmitCheckCPU()
                Case 131
                    'SubmitCheckMemory()
                Case 132
                    'TextFileLogging(Now() & vbCrLf & " SubmitCheckCustom1")
                    'SubmitCheckCustom1()

            End Select
        Catch ex As Exception
            TextFileLogging(ex.Message & vbCrLf & ex.ToString)
        End Try
    End Sub

    Private Sub ErrorLoadingPlugin(ByVal oPath As String, ByVal oType As String) Handles PluginMgmtObj.pluginNotAdded
        EventLogging("Failed to load Plugin" & vbCrLf & "path:" & oPath, "Medium", 207)
        End
    End Sub

#End Region

End Class

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
