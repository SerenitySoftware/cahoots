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