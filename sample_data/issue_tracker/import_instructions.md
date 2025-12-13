Import instructions (quick)
========================

Option A — Create new NSF and import DXL:
1. Open Domino Designer.
2. File -> Application -> New -> create a new application (e.g., issues.nsf).
3. In Designer, use File -> Import -> DXL... (or right-click application -> Import -> DXL).
4. Select IssueForm.dxl and AllIssuesView.dxl and import them.
   - If DXL import fails for views, create a new View named "AllIssues" and set the selection formula to: SELECT Form = "IssueForm"
   - Then add columns as described in the README.
5. Create a new Agent -> Name "CreateIssueAgent" -> choose LotusScript and paste the contents of CreateIssueAgent.lss.
6. Create a Web Agent -> Name "IssuesJSON" -> paste IssuesJSONAgent.lss -> set it to run on web.
7. Sign agents and design elements with an ID that has the required rights.
8. Test by creating an Issue document and running the web agent: http://yourserver/yourdb.nsf/IssuesJSON?OpenAgent

Option B — Create design elements manually:
- Open Designer, create Form named IssueForm and fields according to README.
- Create view AllIssues with selection formula: SELECT Form = "IssueForm"
- Create agents and paste LotusScript.

Need help? Reply and I will:
- produce a full single DXL file for import, or
- produce a Domino Volt JSON scaffold, or
- walk through any import errors you encounter and fix them.
