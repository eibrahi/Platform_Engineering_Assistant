# platforms Specification                                                                                                                             
                                                                                                                                        
## Purpose                                                                                                                                            
Plattformen (zum Beispiel ein Databricks-Workspace wie DBTX_Prod) über die REST-API unter /api/platforms anlegen, lesen, ändern und löschen.          
Plattformen sind der Bezugspunkt für Incidents, Deployments und Unterhaltungen.                                                                       
                                                                                                                                        
## Requirements                                                                                                                                       
                                                                                                                                        
### Requirement: Plattform anlegen                                                                                                                    
Das System SHALL über POST /api/platforms eine Plattform anlegen und sie mit Status 201 zurückgeben. Pflichtfelder sind name (1 bis 100 Zeichen) und  
environment (dev, test oder prod). Ohne Angabe gilt cloud_provider = azure und status = unknown.                                                      
                                                                                                                                        
#### Scenario: Gültige Plattform                                                                                                                      
- **WHEN** ein Client name = DBTX_Prod und environment = prod sendet                                                                                  
- **THEN** antwortet die API mit 201 und liefert die Plattform mit id, cloud_provider = azure, status = unknown, created_at und updated_at            
                                                                                                                                        
#### Scenario: Ungültige Umgebung                                                                                                                     
- **WHEN** ein Client environment = staging sendet                                                                                                    
- **THEN** antwortet die API mit 422                                                                                                                  
                                                                                                                                        
### Requirement: Eindeutiger Plattformname                                                                                                            
Das System MUST doppelte Plattformnamen ablehnen, beim Anlegen und beim Ändern.                                                                       
                                                                                                                                        
#### Scenario: Name bereits vergeben                                                                                                                  
- **WHEN** ein Client eine Plattform mit einem Namen anlegt, den es schon gibt                                                                        
- **THEN** antwortet die API mit 409 und der Meldung "Eine Plattform mit diesem Namen existiert bereits"                                              
                                                                                                                                        
### Requirement: Plattformen auflisten                                                                                                                
Das System SHALL über GET /api/platforms alle Plattformen nach id aufsteigend liefern und optional nach environment filtern.                          
                                                                                                                                        
#### Scenario: Nach Umgebung filtern                                                                                                                  
- **WHEN** ein Client GET /api/platforms?environment=prod aufruft                                                                                     
- **THEN** enthält die Antwort nur Plattformen mit environment = prod              

### Requirement: Einzelne Plattform lesen                                                                                                             
Das System SHALL über GET /api/platforms/{id} eine Plattform liefern und mit 404 antworten, wenn es sie nicht gibt.                                   
                                                                                                                                        
#### Scenario: Unbekannte Plattform                                                                                                                   
- **WHEN** ein Client eine nicht vorhandene id abruft                                                                                                 
- **THEN** antwortet die API mit 404 und der Meldung "Plattform nicht gefunden"                                                                       
                                                                                                                                        
### Requirement: Plattform teilweise ändern                                                                                                           
Das System SHALL über PUT /api/platforms/{id} nur die mitgeschickten Felder ändern. Die Pflichtfelder name, environment, cloud_provider und status    
MUST NOT auf null gesetzt werden.                                                                                                                     
                                                                                                                                        
#### Scenario: Nur den Status ändern                                                                                                                  
- **WHEN** ein Client nur status = degraded sendet                                                                                                    
- **THEN** ändert sich nur der Status, alle anderen Felder bleiben gleich                                                                             
                                                                                                                                        
#### Scenario: Pflichtfeld auf null                                                                                                                   
- **WHEN** ein Client name = null sendet                                                                                                              
- **THEN** antwortet die API mit 422                                                                                                                  
                                                                                                                                        
### Requirement: Plattform löschen                                                                                                                    
Das System SHALL über DELETE /api/platforms/{id} eine Plattform löschen, mit 204 antworten und ihre Incidents und Deployments mitlöschen.             
                                                                                                                                        
#### Scenario: Plattform mit Incidents löschen                                                                                                        
- **WHEN** ein Client eine Plattform löscht, zu der Incidents gehören                                                                                 
- **THEN** antwortet die API mit 204, und die Plattform und ihre Incidents sind weg 
