#!/usr/bin/env python
"""
Application to manage github account.

This is a wrapper around github API v3 using
githubpy library.

"""

from github import GitHub
import argparse
import ConfigParser


def auth_user():
    """
    Authenticate the user.

    Returns JsonObject.

    """
    cfgparser = ConfigParser.ConfigParser()
    cfgparser.readfp(open('login.cfg'))
    user = cfgparser.get('login', 'username')
    passwd = cfgparser.get('login', 'password')
    gh = GitHub(username=user, password=passwd)
    return gh


def list_repos():
    """Provide a list of repositories that the user has created."""
    instance = auth_user()
    repos = instance.user('repos').get(type="owner")
    for repo in repos:
        print "%20s:\t" % repo.name,
        if repo.private:
            print "Private"
        else:
            print "Public"


def create_repo(repo_name, repo_access):
    """Create a new github repository."""
    instance = auth_user()
    created = instance.user('repos').post(name=repo_name, private=repo_access)
    if created:
        print created.clone_url


def list_members(repo_name):
    """List the members who have access to the repository."""
    instance = auth_user()
    user = instance.user().get().login
    collaborators = instance.repos(user)(repo_name).collaborators.get()
    for collaborator in collaborators:
        print collaborator.login


def add_member(repo_name, member):
    """Add given user to access rights to a repository."""
    instance = auth_user()
    user = instance.user().get().login
    instance.repos(user)(repo_name)('collaborators')(member).put()
    print "%s added to repository %s." % (member, repo_name)


def remove_member(repo_name, member):
    """Remove given user from access rights to a repository."""
    instance = auth_user()
    user = instance.user().get().login
    instance.repos(user)(repo_name)('collaborators')(member).delete()
    print "%s removed from repository %s." % (member, repo_name)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--list-repos", action='store_true',
                        help="List repositories belonging to the user.")
    new_repo = parser.add_argument_group('Create Repository')
    new_repo.add_argument("--add-repo", nargs=1,
                          help="""Create a new repository. Optionally
                          specify false for creating a public repo.""")
    new_repo.add_argument("--public", action="store_true",
                          help="Make the repo public.")
    parser.add_argument("--list-members", nargs=1,
                        help="Collaborators assigned to a given repository.")
    collab = parser.add_argument_group("Collaborators")
    manage_collaborator = collab.add_mutually_exclusive_group()
    manage_collaborator.add_argument("--add-collaborator", nargs=1,
                                     help="Add collaborator for the repo.")
    manage_collaborator.add_argument("--remove-collaborator", nargs=1,
                                     help="Remove collaborator from the repo.")
    collab.add_argument("--repo", nargs=1, help="Repo Name")
    values = parser.parse_args()
    if values.list_repos:
        list_repos()
    elif values.add_repo:
        access = not values.public
        create_repo(values.add_repo[0], access)
    elif values.list_members:
        list_members(values.list_members[0])
    elif values.add_collaborator:
        add_member(values.repo[0], values.add_collaborator[0])
    elif values.remove_collaborator:
        remove_member(values.repo[0], values.remove_collaborator[0])
