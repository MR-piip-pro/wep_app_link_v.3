import sqlite3
import csv
import json
import os
import sys
from datetime import datetime

class TerminalLinkManager:
    def __init__(self, db_path='links.db'):
        self.db_path = db_path
        self.init_db()
    
    def init_db(self):
        """Initialize the database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS links (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                description TEXT NOT NULL,
                tags TEXT,
                url TEXT NOT NULL,
                file_group TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        conn.commit()
        conn.close()
    
    def add_link(self, description, tags, url, file_group):
        """Add a new link to the database"""
        if not url.startswith('http://') and not url.startswith('https://'):
            return False, "URL must start with http:// or https://"
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        try:
            cursor.execute('''
                INSERT INTO links (description, tags, url, file_group)
                VALUES (?, ?, ?, ?)
            ''', (description, tags, url, file_group))
            conn.commit()
            conn.close()
            return True, "Link added successfully!"
        except Exception as e:
            conn.close()
            return False, f"Error adding link: {str(e)}"
    
    def get_all_links(self):
        """Get all links from database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM links ORDER BY created_at DESC')
        links = cursor.fetchall()
        conn.close()
        return [{'id': l[0], 'description': l[1], 'tags': l[2], 'url': l[3], 'file_group': l[4], 'created_at': l[5]} for l in links]
    
    def get_links_by_group(self, group):
        """Get links by group"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM links WHERE file_group = ? ORDER BY created_at DESC', (group,))
        links = cursor.fetchall()
        conn.close()
        return [{'id': l[0], 'description': l[1], 'tags': l[2], 'url': l[3], 'file_group': l[4], 'created_at': l[5]} for l in links]
    
    def search_links(self, query):
        """Search links by description, tags, or URL"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            SELECT * FROM links 
            WHERE description LIKE ? OR tags LIKE ? OR url LIKE ?
            ORDER BY created_at DESC
        ''', (f'%{query}%', f'%{query}%', f'%{query}%'))
        links = cursor.fetchall()
        conn.close()
        return [{'id': l[0], 'description': l[1], 'tags': l[2], 'url': l[3], 'file_group': l[4], 'created_at': l[5]} for l in links]
    
    def get_link(self, link_id):
        """Get a specific link by ID"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM links WHERE id = ?', (link_id,))
        link = cursor.fetchone()
        conn.close()
        if link:
            return {'id': link[0], 'description': link[1], 'tags': link[2], 'url': link[3], 'file_group': link[4], 'created_at': link[5]}
        return None
    
    def update_link(self, link_id, description, tags, url, file_group):
        """Update an existing link"""
        if not url.startswith('http://') and not url.startswith('https://'):
            return False, "URL must start with http:// or https://"
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        try:
            cursor.execute('''
                UPDATE links 
                SET description = ?, tags = ?, url = ?, file_group = ?
                WHERE id = ?
            ''', (description, tags, url, file_group, link_id))
            conn.commit()
            conn.close()
            return True, "Link updated successfully!"
        except Exception as e:
            conn.close()
            return False, f"Error updating link: {str(e)}"
    
    def delete_link(self, link_id):
        """Delete a link"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        try:
            cursor.execute('DELETE FROM links WHERE id = ?', (link_id,))
            conn.commit()
            conn.close()
            return True, "Link deleted successfully!"
        except Exception as e:
            conn.close()
            return False, f"Error deleting link: {str(e)}"
    
    def get_groups(self):
        """Get all unique groups"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT DISTINCT file_group FROM links ORDER BY file_group')
        groups = cursor.fetchall()
        conn.close()
        return [g[0] for g in groups]
    
    def get_stats(self):
        """Get statistics about links"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT COUNT(*) FROM links')
        total_links = cursor.fetchone()[0]
        cursor.execute('SELECT COUNT(DISTINCT file_group) FROM links')
        total_groups = cursor.fetchone()[0]
        cursor.execute('''
            SELECT file_group, COUNT(*) as count 
            FROM links 
            GROUP BY file_group 
            ORDER BY count DESC 
            LIMIT 1
        ''')
        most_group = cursor.fetchone()
        conn.close()
        return {
            'total_links': total_links,
            'total_groups': total_groups,
            'most_group': most_group
        }
    
    def export_links(self, filename, format_type):
        """Export links to CSV or JSON"""
        links = self.get_all_links()
        
        if format_type.lower() == 'csv':
            with open(filename, 'w', newline='', encoding='utf-8') as file:
                writer = csv.writer(file)
                writer.writerow(['ID', 'Description', 'Tags', 'URL', 'Group', 'Created At'])
                for link in links:
                    writer.writerow([link['id'], link['description'], link['tags'], link['url'], link['file_group'], link['created_at']])
        elif format_type.lower() == 'json':
            with open(filename, 'w', encoding='utf-8') as file:
                json.dump(links, file, indent=2, ensure_ascii=False)
        else:
            return False, "Unsupported format. Use 'csv' or 'json'."
        
        return True, f"Links exported to {filename} successfully!"

class TerminalInterface:
    def __init__(self):
        self.link_manager = TerminalLinkManager()
        self.colors = {
            'red': '\033[91m',
            'green': '\033[92m',
            'yellow': '\033[93m',
            'blue': '\033[94m',
            'purple': '\033[95m',
            'cyan': '\033[96m',
            'white': '\033[97m',
            'bold': '\033[1m',
            'end': '\033[0m'
        }
    
    def print_colored(self, text, color='white'):
        """Print colored text"""
        print(f"{self.colors.get(color, '')}{text}{self.colors['end']}")
    
    def clear_screen(self):
        """Clear the terminal screen"""
        os.system('clear' if os.name == 'posix' else 'cls')
    
    def print_header(self):
        """Print application header"""
        self.clear_screen()
        self.print_colored("=" * 60, 'cyan')
        self.print_colored("           Web Links Manager - Terminal Version", 'bold')
        self.print_colored("=" * 60, 'cyan')
        print()
    
    def print_menu(self):
        """Print main menu"""
        self.print_colored("Main Menu:", 'yellow')
        print("1. Add new link")
        print("2. View all links")
        print("3. View links by group")
        print("4. Search links")
        print("5. Edit link")
        print("6. Delete link")
        print("7. View statistics")
        print("8. Export links")
        print("9. View groups")
        print("0. Exit")
        print()
    
    def get_user_input(self, prompt):
        """Get user input with colored prompt"""
        return input(f"{self.colors['cyan']}{prompt}{self.colors['end']}: ")
    
    def add_link_interface(self):
        """Interface for adding a new link"""
        self.print_header()
        self.print_colored("Add New Link", 'yellow')
        print()
        
        description = self.get_user_input("Enter description")
        if not description.strip():
            self.print_colored("Description cannot be empty!", 'red')
            input("Press Enter to continue...")
            return
        
        tags = self.get_user_input("Enter tags (optional)")
        url = self.get_user_input("Enter URL")
        file_group = self.get_user_input("Enter group")
        
        success, message = self.link_manager.add_link(description, tags, url, file_group)
        
        if success:
            self.print_colored(message, 'green')
        else:
            self.print_colored(message, 'red')
        
        input("Press Enter to continue...")
    
    def view_links_interface(self, links=None):
        """Interface for viewing links"""
        if links is None:
            links = self.link_manager.get_all_links()
        
        self.print_header()
        self.print_colored(f"Links ({len(links)} total)", 'yellow')
        print()
        
        if not links:
            self.print_colored("No links found.", 'yellow')
            input("Press Enter to continue...")
            return
        
        for link in links:
            self.print_colored(f"ID: {link['id']}", 'cyan')
            self.print_colored(f"Description: {link['description']}", 'white')
            if link['tags']:
                self.print_colored(f"Tags: {link['tags']}", 'purple')
            self.print_colored(f"URL: {link['url']}", 'blue')
            self.print_colored(f"Group: {link['file_group']}", 'green')
            self.print_colored(f"Created: {link['created_at']}", 'yellow')
            print("-" * 50)
        
        input("Press Enter to continue...")
    
    def view_links_by_group_interface(self):
        """Interface for viewing links by group"""
        groups = self.link_manager.get_groups()
        
        if not groups:
            self.print_colored("No groups found.", 'yellow')
            input("Press Enter to continue...")
            return
        
        self.print_header()
        self.print_colored("Available Groups:", 'yellow')
        for i, group in enumerate(groups, 1):
            print(f"{i}. {group}")
        print()
        
        try:
            choice = int(self.get_user_input("Select group number")) - 1
            if 0 <= choice < len(groups):
                links = self.link_manager.get_links_by_group(groups[choice])
                self.view_links_interface(links)
            else:
                self.print_colored("Invalid choice!", 'red')
                input("Press Enter to continue...")
        except ValueError:
            self.print_colored("Please enter a valid number!", 'red')
            input("Press Enter to continue...")
    
    def search_links_interface(self):
        """Interface for searching links"""
        self.print_header()
        self.print_colored("Search Links", 'yellow')
        print()
        
        query = self.get_user_input("Enter search term")
        if not query.strip():
            self.print_colored("Search term cannot be empty!", 'red')
            input("Press Enter to continue...")
            return
        
        links = self.link_manager.search_links(query)
        self.view_links_interface(links)
    
    def edit_link_interface(self):
        """Interface for editing a link"""
        self.print_header()
        self.print_colored("Edit Link", 'yellow')
        print()
        
        try:
            link_id = int(self.get_user_input("Enter link ID to edit"))
            link = self.link_manager.get_link(link_id)
            
            if not link:
                self.print_colored("Link not found!", 'red')
                input("Press Enter to continue...")
                return
            
            self.print_colored("Current link details:", 'cyan')
            print(f"Description: {link['description']}")
            print(f"Tags: {link['tags']}")
            print(f"URL: {link['url']}")
            print(f"Group: {link['file_group']}")
            print()
            
            description = self.get_user_input("Enter new description (or press Enter to keep current)")
            if not description.strip():
                description = link['description']
            
            tags = self.get_user_input("Enter new tags (or press Enter to keep current)")
            if not tags.strip():
                tags = link['tags']
            
            url = self.get_user_input("Enter new URL (or press Enter to keep current)")
            if not url.strip():
                url = link['url']
            
            file_group = self.get_user_input("Enter new group (or press Enter to keep current)")
            if not file_group.strip():
                file_group = link['file_group']
            
            success, message = self.link_manager.update_link(link_id, description, tags, url, file_group)
            
            if success:
                self.print_colored(message, 'green')
            else:
                self.print_colored(message, 'red')
            
            input("Press Enter to continue...")
            
        except ValueError:
            self.print_colored("Please enter a valid ID!", 'red')
            input("Press Enter to continue...")
    
    def delete_link_interface(self):
        """Interface for deleting a link"""
        self.print_header()
        self.print_colored("Delete Link", 'yellow')
        print()
        
        try:
            link_id = int(self.get_user_input("Enter link ID to delete"))
            link = self.link_manager.get_link(link_id)
            
            if not link:
                self.print_colored("Link not found!", 'red')
                input("Press Enter to continue...")
                return
            
            self.print_colored("Link to delete:", 'red')
            print(f"Description: {link['description']}")
            print(f"URL: {link['url']}")
            print()
            
            confirm = self.get_user_input("Are you sure? (yes/no)")
            if confirm.lower() in ['yes', 'y']:
                success, message = self.link_manager.delete_link(link_id)
                if success:
                    self.print_colored(message, 'green')
                else:
                    self.print_colored(message, 'red')
            else:
                self.print_colored("Deletion cancelled.", 'yellow')
            
            input("Press Enter to continue...")
            
        except ValueError:
            self.print_colored("Please enter a valid ID!", 'red')
            input("Press Enter to continue...")
    
    def view_stats_interface(self):
        """Interface for viewing statistics"""
        stats = self.link_manager.get_stats()
        
        self.print_header()
        self.print_colored("Statistics", 'yellow')
        print()
        
        self.print_colored(f"Total Links: {stats['total_links']}", 'cyan')
        self.print_colored(f"Total Groups: {stats['total_groups']}", 'cyan')
        
        if stats['most_group']:
            self.print_colored(f"Most Popular Group: {stats['most_group'][0]} ({stats['most_group'][1]} links)", 'cyan')
        else:
            self.print_colored("Most Popular Group: None", 'cyan')
        
        print()
        input("Press Enter to continue...")
    
    def export_links_interface(self):
        """Interface for exporting links"""
        self.print_header()
        self.print_colored("Export Links", 'yellow')
        print()
        
        print("Available formats: CSV, JSON")
        format_type = self.get_user_input("Enter format").lower()
        
        if format_type not in ['csv', 'json']:
            self.print_colored("Unsupported format!", 'red')
            input("Press Enter to continue...")
            return
        
        filename = self.get_user_input("Enter filename")
        if not filename.strip():
            self.print_colored("Filename cannot be empty!", 'red')
            input("Press Enter to continue...")
            return
        
        if not filename.endswith(f'.{format_type}'):
            filename += f'.{format_type}'
        
        success, message = self.link_manager.export_links(filename, format_type)
        
        if success:
            self.print_colored(message, 'green')
        else:
            self.print_colored(message, 'red')
        
        input("Press Enter to continue...")
    
    def view_groups_interface(self):
        """Interface for viewing groups"""
        groups = self.link_manager.get_groups()
        
        self.print_header()
        self.print_colored("Available Groups", 'yellow')
        print()
        
        if not groups:
            self.print_colored("No groups found.", 'yellow')
        else:
            for i, group in enumerate(groups, 1):
                links = self.link_manager.get_links_by_group(group)
                self.print_colored(f"{i}. {group} ({len(links)} links)", 'cyan')
        
        print()
        input("Press Enter to continue...")
    
    def run(self):
        """Main application loop"""
        while True:
            self.print_header()
            self.print_menu()
            
            choice = self.get_user_input("Enter your choice")
            
            if choice == '1':
                self.add_link_interface()
            elif choice == '2':
                self.view_links_interface()
            elif choice == '3':
                self.view_links_by_group_interface()
            elif choice == '4':
                self.search_links_interface()
            elif choice == '5':
                self.edit_link_interface()
            elif choice == '6':
                self.delete_link_interface()
            elif choice == '7':
                self.view_stats_interface()
            elif choice == '8':
                self.export_links_interface()
            elif choice == '9':
                self.view_groups_interface()
            elif choice == '0':
                self.print_colored("Goodbye!", 'green')
                break
            else:
                self.print_colored("Invalid choice! Please try again.", 'red')
                input("Press Enter to continue...")

def main():
    """Main function"""
    try:
        app = TerminalInterface()
        app.run()
    except KeyboardInterrupt:
        print("\n\nGoodbye!")
        sys.exit(0)
    except Exception as e:
        print(f"An error occurred: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main() 