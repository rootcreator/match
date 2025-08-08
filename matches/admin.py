from django.contrib import admin
from django.core.management import call_command
from .models import Team, Player, Match, Prediction, Fixture, UserPrediction, Bet
from matches.logic.train_and_predict import train_and_predict

from django.urls import path
from django.shortcuts import render, redirect
from django.core.management import call_command
from django.contrib import messages
from .models import Team

# Import major leagues from your sync_teams command
from matches.management.commands.sync_teams import Command as SyncTeamsCommand

@admin.register(Team)
class TeamAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "league", "api_id")
    search_fields = ("name", "league")

    change_list_template = "admin/team_changelist.html"

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path("sync_teams_form/", self.admin_site.admin_view(self.sync_teams_form), name="sync_teams_form"),
        ]
        return custom_urls + urls

    def sync_teams_form(self, request):
        if request.method == "POST":
            league_slug = request.POST.get("league")
            season = request.POST.get("season")

            if not league_slug or not season:
                messages.error(request, "Please select both league and season.")
            else:
                call_command("sync_teams", f"--{league_slug}", "--season", season)
                messages.success(
                    request,
                    f"✅ Teams synced successfully for {league_slug.replace('-', ' ').title()} ({season})"
                )
                return redirect("..")

        # ✅ Build a dummy parser to trigger add_arguments and get league_map
        from argparse import ArgumentParser
        temp_cmd = SyncTeamsCommand()
        parser = ArgumentParser()
        temp_cmd.add_arguments(parser)
        league_options = sorted(temp_cmd.league_map.keys())

        return render(request, "admin/sync_teams_form.html", {
            "title": "Sync Teams from API",
            "league_options": league_options,
        })




@admin.register(Player)
class PlayerAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "team", "position", "injured")
    list_filter = ("position", "injured", "team")
    search_fields = ("name",)
    actions = ["sync_players_action"]

    def sync_players_action(self, request, queryset):
        from django.core.management import call_command
        call_command("sync_players")
        self.message_user(request, "✅ Players synced for all teams.")

    sync_players_action.short_description = "Sync Players for All Teams"


@admin.register(Fixture)
class FixtureAdmin(admin.ModelAdmin):
    list_display = ("id", "date", "status", "home_team", "away_team")
    list_filter = ("status", "date")
    search_fields = ("home_team__name", "away_team__name")
    actions = ["sync_upcoming_fixtures_action"]

    def sync_upcoming_fixtures_action(self, request, queryset):
        call_command("sync_upcoming_fixtures")
        self.message_user(request, "✅ Upcoming fixtures synced successfully.")

    sync_upcoming_fixtures_action.short_description = "Sync Upcoming Fixtures from API"


@admin.register(Match)
class MatchAdmin(admin.ModelAdmin):
    list_display = ("id", "fixture_id", "home_team", "away_team", "date", "result")
    list_filter = ("result", "date")
    search_fields = ("home_team__name", "away_team__name")
    actions = ["run_training_and_prediction", "sync_past_matches_action"]

    def run_training_and_prediction(self, request, queryset):
        result = train_and_predict()
        if result.get("status") == "success":
            self.message_user(
                request,
                f"✅ Training complete. Accuracy: {result['accuracy']} | Matches predicted: {result['matches_predicted']}"
            )
        else:
            self.message_user(
                request,
                f"❌ Failed: {result.get('reason', 'Unknown error')}",
                level="error"
            )

    run_training_and_prediction.short_description = "Train & Predict Upcoming Matches"

    def sync_past_matches_action(self, request, queryset):
        call_command("sync_past_matches")
        self.message_user(request, "✅ Past matches synced successfully.")

    sync_past_matches_action.short_description = "Sync Past Matches from API"


@admin.register(Prediction)
class PredictionAdmin(admin.ModelAdmin):
    list_display = (
        "fixture", "result_pred", "confidence", "goal_diff",
        "fair_odds_home", "fair_odds_draw", "fair_odds_away", "model_version"
    )
    list_filter = ("result_pred", "model_version")
    search_fields = ("match__home_team__name", "match__away_team__name")


@admin.register(UserPrediction)
class UserPredictionAdmin(admin.ModelAdmin):
    list_display = ("user", "match", "predicted_result", "created_at")
    list_filter = ("predicted_result", "created_at")
    search_fields = ("user__username", "match__home_team__name", "match__away_team__name")


@admin.register(Bet)
class BetAdmin(admin.ModelAdmin):
    list_display = (
        "user", "match", "predicted_result", "amount", "odds",
        "is_settled", "win", "payout", "placed_at"
    )
    list_filter = ("is_settled", "win", "placed_at")
    search_fields = ("user__username", "match__home_team__name", "match__away_team__name")
