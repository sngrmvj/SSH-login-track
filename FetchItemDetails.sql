

-- My Items
-- Page tracking is done by the application, If the previous page is My Items following are the queries
SELECT game_type FROM Item WHERE Item.itemno='$itemno';


-- If the item is Card ot Board
SELECT Item.itemno, Item.title, Item.description, Item.game_type ,Item.condition_type FROM Item WHERE Item.itemno ='$itemno';

-- If the item is Video
SELECT Item.itemno, Item.title, Item.description, Item.game_type ,Item.condition_type, VideoPlatform.platform_name, Video.media_type 
FROM Item 
INNER JOIN Video ON Item.itemno = Video.itemno 
INNER JOIN VideoPlatform ON Video.platform_id = VideoPlatfrom.platform_id WHERE Item.itemno='$itemno';

-- If the item is JigsawItem
SELECT Item.itemno, Item.title, Item.description, Item.game_type ,Item.condition_type, JigsawItem.piece_count
FROM Item INNER JOIN JigsawItem ON Item.itemno = JigsawItem.itemno WHERE Item.itemno='$itemno';

-- If the item is Computer
SELECT Item.itemno, Item.title, Item.description, Item.game_type ,Item.condition_type, Computer.platform_name
FROM Item INNER JOIN Computer ON Item.itemno = Computer.itemno WHERE Item.itemno='$itemno';



-- If the previous page is Search Items
-- Getting game_type to figure what the type of the game initially from the itemno
SELECT game_type, email FROM Item WHERE Item.itemno='$itemno';
-- Getting the itmeno as cpitemno which se use it for fetching the counterparty rating based on the email
SELECT itemno AS cpitemno FROM Item WHERE Item.email = '$email';

-- If the item is Card ot Board
SELECT Item.itemno, Item.title, Item.description, Item.game_type ,Item.condition_type FROM Item WHERE Item.itemno ='$itemno';

-- If the item is Video
SELECT Item.itemno, Item.title, Item.description, Item.game_type ,Item.condition_type, VideoPlatform.platform_name, Video.media_type 
FROM Item 
INNER JOIN Video ON Item.itemno = Video.itemno 
INNER JOIN VideoPlatform ON Video.platform_id = VideoPlatfrom.platform_id WHERE Item.itemno='$itemno';

-- If the item is Jigsaw
SELECT Item.itemno, Item.title, Item.description, Item.game_type ,Item.condition_type, JigsawItem.piece_count
FROM Item INNER JOIN JigsawItem ON Item.itemno = JigsawItem.itemno WHERE Item.itemno='$itemno';

-- If the item is Computer
SELECT Item.itemno, Item.title, Item.description, Item.game_type ,Item.condition_type, Computer.platform_name
FROM Item INNER JOIN Computer ON Item.itemno = Computer.itemno WHERE Item.itemno='$itemno';

-- we need to join with the tables i feel we don't have to use the CASE here.
SELECT avg(ratings) FROM Swap WHERE Swap.cpitemno = '$cpitemno';

-- This is to get the details of the counter party
SELECT User.nick_name, Address.city, Address.state, User.postalcode
FROM User INNER JOIN Address ON User.postalcode = Address.postalcode WHERE User.email = '$email';

-- This is to get the details of the party for distance
SELECT Address.city, Address.state, User.postalcode
FROM User INNER JOIN Address On User.postalcode = Address.postalcode WHERE User.email = '$currentemail';