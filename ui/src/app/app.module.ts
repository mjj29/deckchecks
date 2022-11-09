import { NgModule } from '@angular/core';
import { BrowserModule } from '@angular/platform-browser';

// services
import { PairingsService } from './apis/pairings/pairings.service';
import { ChecksService } from './apis/checks/checks.service';
import { ListService } from './apis/list/list.service';
import { ListsService } from './apis/lists/lists.service';
import { MissingService } from './apis/missing/missing.service';
import { PlayerService } from './apis/player/player.service';
import { RecommendsService } from './apis/recommend/recommend.service';
import { SettingsService } from './apis/settings/settings.service';
import { TableService } from './apis/table/table.service';
import { TopService } from './apis/top/top.service';

// components
import { AppComponent } from './app.component';
import { PairingsComponent } from './components/pairings/pairings.component';

@NgModule({
  declarations: [
    AppComponent,
    PairingsComponent
  ],
  imports: [
    BrowserModule
  ],
  providers: [
	  PairingsService,
	  ChecksService,
	  ListService,
	  ListsService,
	  MissingService,
	  PlayerService,
	  RecommendsService,
	  SettingsService,
	  TableService,
	  TopService
  ],
  bootstrap: [
	  AppComponent,
	  PairingsService
  ]
})
export class AppModule { }
