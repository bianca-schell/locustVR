turn on observation cam first, then recording control
output of the script can be seen:

either (when run via motif recording system) clicking in the supervisor 5th line experiments master OR

***run experiment via terminal with commands:
source ~/Development/sphevr/venv/bin/activate
python ~/Documents/locustVR/experiments/test_rendered4.py


#path geaendert- wenn das ein problem macht dann wieder experiments zurück in Docu/experiments

#stimulus input without database interaction ---> manually_moving_posts.py



************** HINTS *****************
wirte in db deaktiviert #e.writeInDb()

experimentBase script is in
development locustvr/experiment/base.py



stimulus_osg is in development/freemovrprivate/src/freemovr/proxy


wenn locustVR cam_control ausgeschaltet ist, wird die position des locust in der vr nicht aktualisiert: um auf 0,0 zu resetten: locustVR cam_control eingeschalten

wenn camcontrol nicht funktioniert: zum änern der locust position funktioniert auch  	locustvr-debug-random-control im supervisor administraion


im skript keine notizen mit sonderzeichen!!!!!!!!!!!!!!!!!!!!!!!!!!!
bei random error: vllt db voll!

********recreate db**************
changes in dbGen/dbGen.py
cd dbGen/

start python
    import dbGen
    run : dbGen.FirstGen()


run python dbGen.py
copy dbs to databases folder

#*****************github

#to get a github repository locally
git clone <link>

#to send local changes to remote repository
git add . #adds all changes
OR
git add <file to add> #adds changes in specific file

git commit -m "msg"

git push

#to import changes from remote repository locally
git pull



*************** TODO *****************

# setting up experiment: calling posts after each other for certain time, delay period...
# find out how to put  cntr for every reset of position, maybe direction of animal
# vermutlich sinnvoll runforever aufzuloesen              


DONE
 # in db nur einmal pro experiment rein schreiben, nicht die ganze zeit., jede uniqueID in db nur einmal vorhanden
# folder that contains csv file should have the name of the uniqueID
   # path kreieren in dem csv file erstellt wird wie in flyVR ganz am anfang
            
# write actual position not just once. in interact-csv-create gives the actual position as print


#like this it's overwriting the position all the time**************************************in while loop it doesnt get the new pos.

  # change the path of csv, db ...
                
         # find out how to put coordinates        



