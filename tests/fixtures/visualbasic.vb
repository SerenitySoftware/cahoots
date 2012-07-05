Public Class About
    Private Sub About_Load(sender As Object, e As EventArgs) Handles MyBase.Load
        ToolTip1.SetToolTip(Label1, "Last compatible game version: June BWE Update")
        ToolTip1.SetToolTip(Label2, "Close")
        ToolTip1.SetToolTip(LinkLabel1, "Homepage")
        ToolTip1.SetToolTip(LinkLabel2, "Click to view the full license")
    End Sub

    Private Sub Label2_Click(sender As Object, e As EventArgs) Handles Label2.Click
        Me.Close()
    End Sub

    Private Sub LinkLabel1_LinkClicked(sender As Object, e As LinkLabelLinkClickedEventArgs) Handles LinkLabel1.LinkClicked
        Process.Start("http://www.falchibianchi.enjin.com")
    End Sub

    Private Sub LinkLabel2_LinkClicked(sender As Object, e As LinkLabelLinkClickedEventArgs) Handles LinkLabel2.LinkClicked
        Process.Start("http://en.wikipedia.org/wiki/MIT_License")
    End Sub
End Class