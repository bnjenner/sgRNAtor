# sgRNAtor

Bioinformatics Challenge Project investigating subgenomic RNA in SARS-CoV-2.

## Organization Workflow
### File Tracking
This repository is only intended to track scripts, configs, metadata, and certain summary 
reports. All data files are set to be ignored by default, although this is accomplished through
regular expression patterns in the ".gitignore" file, not by file size.

To view the list of excluded patterns, run this command in the root of this repository.
```
cat .gitignore
```

To view untracked files not excluded by .gitignore, run:
```
git ls-files --others --exclude-standard
```

If you generate a data file that is not excluded by patterns in the .gitignore file, please consider
adding it to the list before staging and commiting changes.

### Branches
All users working in their individual user directories should work on their own branch.
This prevents conflicts as we all work independently in the beginning stages of our
analysis. Directly pushing to the main branch has also been disabled.

To create and begin working on your branch, run this command.
```
git checkout -b $USER
```

After changes have been staged and commited, push to remote using this command.
```
git push origin $USER
```

### Pull Requests
Since all contributions to the main branch have been disabled, integrating new
features and commits must be done through pull requests. This should be done
only after communicating the intended changes to the group, although there
are no branch rules in place to enfore this. 

Future contributions to our combined analysis will also be implemented using branches and pull requests. 
